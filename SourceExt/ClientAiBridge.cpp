#include "ClientExtension.h"

#if !FO_WEB && !FO_IOS && !FO_ANDROID

#include "Logging.h"

#include "asio.hpp"
#include "json.hpp"

#endif

FO_USING_NAMESPACE();

FO_BEGIN_NAMESPACE
///@ ExportMethod
FO_SCRIPT_API bool Client_Game_AiControlStart(ClientEngine* client, bool enabled, string_view host, int32_t port, string_view token, int32_t maxQueuedCommands, int32_t maxEvents);
///@ ExportMethod
FO_SCRIPT_API void Client_Game_AiControlStop(ClientEngine* client);
///@ ExportMethod
FO_SCRIPT_API bool Client_Game_AiControlIsRunning(ClientEngine* client);
///@ ExportMethod
FO_SCRIPT_API bool Client_Game_AiControlPullCommand(ClientEngine* client, uint32_t& commandSeq, string& type, ident_t& targetId, ident_t& itemId, ident_t& auxId, int32_t& hexX, int32_t& hexY, int32_t& screenX, int32_t& screenY, int32_t& intArg, string& stringArg, bool& append);
///@ ExportMethod
FO_SCRIPT_API void Client_Game_AiControlSetObservation(ClientEngine* client, string_view observationJson);
///@ ExportMethod
FO_SCRIPT_API void Client_Game_AiControlPushEvent(ClientEngine* client, string_view eventJson);
///@ ExportMethod
FO_SCRIPT_API void Client_Game_AiControlCompleteCommand(ClientEngine* client, uint32_t commandSeq, bool success, string_view message);
///@ ExportMethod
FO_SCRIPT_API string Client_Game_AiControlGetStatus(ClientEngine* client);
///@ ExportMethod
FO_SCRIPT_API ident_t Client_Game_AiControlGetEntityId(ClientEngine* client, FO_NULLABLE ClientEntity* entity);
FO_END_NAMESPACE

#if !FO_WEB && !FO_IOS && !FO_ANDROID

struct AiControlCommand
{
    uint32_t Seq {};
    string Type {};
    ident_t TargetId {};
    ident_t ItemId {};
    ident_t AuxId {};
    int32_t HexX {};
    int32_t HexY {};
    int32_t ScreenX {};
    int32_t ScreenY {};
    int32_t IntArg {};
    string StringArg {};
    bool Append {};
};

struct AiControlEvent
{
    uint64_t Seq {};
    string Json {};
};

struct AiControlClientData
{
    mutex Locker {};
    thread Thread {};
    std::atomic_bool StopRequested {};
    std::atomic_bool Running {};
    // Host/Port/Token/MaxQueuedCommands/MaxEvents are set once before the bridge thread starts and then
    // read-only (in the thread and under the lock), so they are not Locker-guarded.
    string Host {};
    uint16_t Port {};
    string Token {};
    size_t MaxQueuedCommands {};
    size_t MaxEvents {};
    uint32_t NextCommandSeq FO_TSA_GUARDED_BY(Locker) {};
    uint64_t NextEventSeq FO_TSA_GUARDED_BY(Locker) {};
    uint64_t ObservationSeq FO_TSA_GUARDED_BY(Locker) {};
    string ObservationJson FO_TSA_GUARDED_BY(Locker) {"{}"};
    deque<AiControlCommand> Commands FO_TSA_GUARDED_BY(Locker) {};
    deque<AiControlEvent> Events FO_TSA_GUARDED_BY(Locker) {};
    string LastError FO_TSA_GUARDED_BY(Locker) {};
    string LogCallbackKey {};
};

static void StopAiControlBridge(AiControlClientData& data) noexcept;
static void RunAiControlBridge(AiControlClientData& data);
static auto HandleAiControlLine(AiControlClientData& data, string_view line, bool& authorized) -> string;
static auto BuildAiControlResponse(const nlohmann::json& id, nlohmann::json result) -> string;
static auto BuildAiControlError(const nlohmann::json& id, int32_t code, string_view message) -> string;
static auto BuildAiControlStatus(AiControlClientData& data) -> nlohmann::json;
static auto BuildAiControlObservation(AiControlClientData& data) -> nlohmann::json;
static auto BuildAiControlEvents(AiControlClientData& data, uint64_t after_seq, size_t limit) -> nlohmann::json;
static auto EnqueueAiControlCommand(AiControlClientData& data, const nlohmann::json& id, const nlohmann::json& params) -> string;
static auto EnsureAiControlData(ClientEngine* client) -> AiControlClientData&;
static auto JsonDumpToString(const nlohmann::json& value) -> string;
static auto GetJsonString(const nlohmann::json& object, string_view name, string_view def_value = {}) -> string;
static auto GetJsonBool(const nlohmann::json& object, string_view name, bool def_value = false) -> bool;
static auto GetJsonInt32(const nlohmann::json& object, string_view name, int32_t def_value = 0) -> int32_t;
static auto GetJsonUInt64(const nlohmann::json& object, string_view name, uint64_t def_value = 0) -> uint64_t;
static auto GetJsonIdent(const nlohmann::json& object, string_view name) -> ident_t;
static void PushAiControlEvent(AiControlClientData& data, string_view event_json);
static void RegisterAiControlLogCallback(AiControlClientData& data);
static void UnregisterAiControlLogCallback(AiControlClientData& data) noexcept;
static auto TryBuildAiControlLogExceptionEvent(LogType type, string_view message, const CatchedStackTraceData* st) -> std::optional<string>;
static auto ClassifyAiControlLogException(LogType type, string_view message) -> string;
static auto LogTypeToString(LogType type) noexcept -> string_view;
static auto TrimAiControlLogMessage(string_view message) -> string;
static bool ContainsCaseInsensitive(string_view text, string_view needle) noexcept;

bool FO_NAMESPACE Client_Game_AiControlStart(ClientEngine* client, bool enabled, string_view host, int32_t port, string_view token, int32_t maxQueuedCommands, int32_t maxEvents)
{
    FO_STACK_TRACE_ENTRY();

    AiControlClientData& data = EnsureAiControlData(client);

    StopAiControlBridge(data);

    if (!enabled) {
        return false;
    }

    if (port <= 0 || port > std::numeric_limits<uint16_t>::max()) {
        throw ScriptException("Invalid AiControl port", port);
    }

    data.StopRequested.store(false, std::memory_order_release);
    data.Host = host.empty() ? "127.0.0.1" : string(host);
    data.Port = numeric_cast<uint16_t>(port);
    data.Token = string(token);
    data.MaxQueuedCommands = numeric_cast<size_t>(std::max(maxQueuedCommands, 1));
    data.MaxEvents = numeric_cast<size_t>(std::max(maxEvents, 1));

    {
        scoped_lock locker(data.Locker);
        data.LastError.clear();
    }

    data.Running.store(true, std::memory_order_release);
    RegisterAiControlLogCallback(data);
    data.Thread = run_thread("AiControl", [&data] { RunAiControlBridge(data); });

    return true;
}

void FO_NAMESPACE Client_Game_AiControlStop(ClientEngine* client)
{
    FO_STACK_TRACE_ENTRY();

    AiControlClientData& data = EnsureAiControlData(client);
    StopAiControlBridge(data);
}

bool FO_NAMESPACE Client_Game_AiControlIsRunning(ClientEngine* client)
{
    FO_STACK_TRACE_ENTRY();

    AiControlClientData& data = EnsureAiControlData(client);
    return data.Running.load(std::memory_order_acquire) && !data.StopRequested.load(std::memory_order_acquire);
}

bool FO_NAMESPACE Client_Game_AiControlPullCommand(ClientEngine* client, uint32_t& commandSeq, string& type, ident_t& targetId, ident_t& itemId, ident_t& auxId, int32_t& hexX, int32_t& hexY, int32_t& screenX, int32_t& screenY, int32_t& intArg, string& stringArg, bool& append)
{
    FO_STACK_TRACE_ENTRY();

    AiControlClientData& data = EnsureAiControlData(client);
    scoped_lock locker(data.Locker);

    if (data.Commands.empty()) {
        return false;
    }

    const AiControlCommand command = std::move(data.Commands.front());
    data.Commands.pop_front();

    commandSeq = command.Seq;
    type = command.Type;
    targetId = command.TargetId;
    itemId = command.ItemId;
    auxId = command.AuxId;
    hexX = command.HexX;
    hexY = command.HexY;
    screenX = command.ScreenX;
    screenY = command.ScreenY;
    intArg = command.IntArg;
    stringArg = command.StringArg;
    append = command.Append;

    return true;
}

void FO_NAMESPACE Client_Game_AiControlSetObservation(ClientEngine* client, string_view observationJson)
{
    FO_STACK_TRACE_ENTRY();

    AiControlClientData& data = EnsureAiControlData(client);
    scoped_lock locker(data.Locker);

    data.ObservationSeq++;
    data.ObservationJson = observationJson.empty() ? "{}" : string(observationJson);
}

void FO_NAMESPACE Client_Game_AiControlPushEvent(ClientEngine* client, string_view eventJson)
{
    FO_STACK_TRACE_ENTRY();

    AiControlClientData& data = EnsureAiControlData(client);
    PushAiControlEvent(data, eventJson);
}

void FO_NAMESPACE Client_Game_AiControlCompleteCommand(ClientEngine* client, uint32_t commandSeq, bool success, string_view message)
{
    FO_STACK_TRACE_ENTRY();

    AiControlClientData& data = EnsureAiControlData(client);

    nlohmann::json event;
    event["type"] = "command_completed";
    event["commandSeq"] = commandSeq;
    event["success"] = success;
    event["message"] = std::string(message);

    PushAiControlEvent(data, JsonDumpToString(event));
}

string FO_NAMESPACE Client_Game_AiControlGetStatus(ClientEngine* client)
{
    FO_STACK_TRACE_ENTRY();

    AiControlClientData& data = EnsureAiControlData(client);
    return JsonDumpToString(BuildAiControlStatus(data));
}

ident_t FO_NAMESPACE Client_Game_AiControlGetEntityId(ClientEngine* client, ClientEntity* entity)
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(client);

    return entity != nullptr ? entity->GetId() : ident_t {};
}

static auto EnsureAiControlData(ClientEngine* client) -> AiControlClientData&
{
    FO_STACK_TRACE_ENTRY();

    ClientExtData& ext = GetClientExtData(client);

    if (!ext.AiControl) {
        ext.AiControl = unique_del_ptr<AiControlClientData>(SafeAlloc::MakeRaw<AiControlClientData>(), [](AiControlClientData* ptr) FO_DEFERRED {
            FO_STACK_TRACE_ENTRY();

            if (ptr != nullptr) {
                StopAiControlBridge(*ptr);
                delete ptr;
            }
        });
    }

    return *ext.AiControl.get();
}

static void StopAiControlBridge(AiControlClientData& data) noexcept
{
    FO_NO_STACK_TRACE_ENTRY();

    data.StopRequested.store(true, std::memory_order_release);
    UnregisterAiControlLogCallback(data);

    if (data.Thread.joinable()) {
        data.Thread.join();
    }

    data.Running.store(false, std::memory_order_release);
}

static void RunAiControlBridge(AiControlClientData& data)
{
    FO_STACK_TRACE_ENTRY();

    try {
        asio::io_context context;
        asio::ip::address address = asio::ip::make_address(data.Host);
        asio::ip::tcp::endpoint endpoint(address, data.Port);
        asio::ip::tcp::acceptor acceptor(context);

        acceptor.open(endpoint.protocol());
        acceptor.set_option(asio::ip::tcp::acceptor::reuse_address(true));
        acceptor.bind(endpoint);
        acceptor.listen();
        acceptor.non_blocking(true);

        string input;
        bool authorized = data.Token.empty();
        unique_ptr<asio::ip::tcp::socket> socket;

        while (!data.StopRequested.load(std::memory_order_acquire)) {
            if (!socket) {
                socket = SafeAlloc::MakeUnique<asio::ip::tcp::socket>(context);

                std::error_code accept_error;
                acceptor.accept(*socket, accept_error);

                if (accept_error == asio::error::would_block || accept_error == asio::error::try_again) {
                    socket.reset();
                    std::this_thread::sleep_for(std::chrono::milliseconds(50));
                    continue;
                }
                if (accept_error) {
                    throw std::runtime_error(std::string(strex("AiControl accept failed: {}", accept_error.message()).str()));
                }

                socket->non_blocking(true);
                input.clear();
                authorized = data.Token.empty();
                continue;
            }

            char buffer[4096] {};
            std::error_code read_error;
            const size_t read_size = socket->read_some(asio::buffer(buffer), read_error);

            if (read_error == asio::error::would_block || read_error == asio::error::try_again) {
                std::this_thread::sleep_for(std::chrono::milliseconds(10));
                continue;
            }
            if (read_error == asio::error::eof || read_error == asio::error::connection_reset || read_error == asio::error::operation_aborted) {
                socket.reset();
                continue;
            }
            if (read_error) {
                throw std::runtime_error(std::string(strex("AiControl read failed: {}", read_error.message()).str()));
            }

            input.append(buffer, read_size);

            if (input.size() > 1024 * 1024) {
                {
                    scoped_lock locker(data.Locker);
                    data.LastError = strex("AiControl input exceeded 1 MiB cap ({} bytes); dropping connection", input.size()).str();
                }

                string error_response = BuildAiControlError(nullptr, -32600, "Request too large");
                error_response += "\n";

                std::error_code write_error;
                socket->non_blocking(false);
                (void)asio::write(*socket, asio::buffer(error_response), write_error);
                socket->non_blocking(true);
                ignore_unused(write_error);

                socket.reset();
                continue;
            }

            while (true) {
                const size_t line_end = input.find('\n');

                if (line_end == string::npos) {
                    break;
                }

                string line = input.substr(0, line_end);
                input.erase(0, line_end + 1);

                if (!line.empty() && line.back() == '\r') {
                    line.pop_back();
                }

                string response = HandleAiControlLine(data, line, authorized);

                if (!response.empty()) {
                    response += "\n";
                    socket->non_blocking(false);
                    asio::write(*socket, asio::buffer(response));
                    socket->non_blocking(true);
                }
            }
        }
    }
    catch (const std::exception& ex) {
        scoped_lock locker(data.Locker);
        data.LastError = string(ex.what());
    }

    data.Running.store(false, std::memory_order_release);
}

static auto HandleAiControlLine(AiControlClientData& data, string_view line, bool& authorized) -> string
{
    FO_STACK_TRACE_ENTRY();

    if (line.empty()) {
        return {};
    }

    nlohmann::json request;

    try {
        request = nlohmann::json::parse(line);
    }
    catch (const std::exception& ex) {
        return BuildAiControlError(nullptr, -32700, strex("Parse error: {}", ex.what()).str());
    }

    const nlohmann::json id = request.contains("id") ? request["id"] : nlohmann::json(nullptr);
    const string method = GetJsonString(request, "method");
    const nlohmann::json params = request.contains("params") && request["params"].is_object() ? request["params"] : nlohmann::json::object();

    if (method.empty()) {
        return BuildAiControlError(id, -32600, "Missing method");
    }

    if (method == "auth") {
        const string token = GetJsonString(params, "token");
        authorized = data.Token.empty() || token == data.Token;
        return BuildAiControlResponse(id, nlohmann::json {{"authorized", authorized}});
    }

    if (!authorized) {
        return BuildAiControlError(id, -32001, "Unauthorized");
    }

    if (method == "ping") {
        return BuildAiControlResponse(id, nlohmann::json {{"ok", true}});
    }
    if (method == "status") {
        return BuildAiControlResponse(id, BuildAiControlStatus(data));
    }
    if (method == "observe") {
        return BuildAiControlResponse(id, BuildAiControlObservation(data));
    }
    if (method == "events") {
        const uint64_t after_seq = GetJsonUInt64(params, "afterSeq");
        const int32_t requested_limit = GetJsonInt32(params, "limit", 100);
        const size_t limit = numeric_cast<size_t>(std::clamp(requested_limit, 1, 500));
        return BuildAiControlResponse(id, BuildAiControlEvents(data, after_seq, limit));
    }
    if (method == "act") {
        return EnqueueAiControlCommand(data, id, params);
    }

    return BuildAiControlError(id, -32601, "Unknown method");
}

static auto EnqueueAiControlCommand(AiControlClientData& data, const nlohmann::json& id, const nlohmann::json& params) -> string
{
    FO_STACK_TRACE_ENTRY();

    AiControlCommand command;
    command.Type = GetJsonString(params, "type");

    if (command.Type.empty()) {
        return BuildAiControlError(id, -32602, "Missing command type");
    }

    command.TargetId = GetJsonIdent(params, "targetId");
    command.ItemId = GetJsonIdent(params, "itemId");
    command.AuxId = GetJsonIdent(params, "auxId");
    command.HexX = GetJsonInt32(params, "x");
    command.HexY = GetJsonInt32(params, "y");
    command.ScreenX = GetJsonInt32(params, "screenX");
    command.ScreenY = GetJsonInt32(params, "screenY");
    command.IntArg = GetJsonInt32(params, "intArg");
    command.StringArg = GetJsonString(params, "stringArg");
    command.Append = GetJsonBool(params, "append");

    {
        scoped_lock locker(data.Locker);

        if (data.Commands.size() >= data.MaxQueuedCommands) {
            return BuildAiControlError(id, -32002, "Command queue is full");
        }

        data.NextCommandSeq++;
        command.Seq = data.NextCommandSeq;
        const uint32_t queued_seq = command.Seq;
        data.Commands.emplace_back(std::move(command));

        return BuildAiControlResponse(id, nlohmann::json {{"accepted", true}, {"commandSeq", queued_seq}});
    }
}

static auto BuildAiControlResponse(const nlohmann::json& id, nlohmann::json result) -> string
{
    FO_STACK_TRACE_ENTRY();

    nlohmann::json response;
    response["jsonrpc"] = "2.0";
    response["id"] = id;
    response["result"] = std::move(result);
    return JsonDumpToString(response);
}

static auto BuildAiControlError(const nlohmann::json& id, int32_t code, string_view message) -> string
{
    FO_STACK_TRACE_ENTRY();

    nlohmann::json response;
    response["jsonrpc"] = "2.0";
    response["id"] = id;
    response["error"] = {{"code", code}, {"message", std::string(message)}};
    return JsonDumpToString(response);
}

static auto BuildAiControlStatus(AiControlClientData& data) -> nlohmann::json
{
    FO_STACK_TRACE_ENTRY();

    scoped_lock locker(data.Locker);

    nlohmann::json status;
    status["running"] = data.Running.load(std::memory_order_acquire);
    status["host"] = std::string(data.Host);
    status["port"] = data.Port;
    status["queuedCommands"] = data.Commands.size();
    status["maxQueuedCommands"] = data.MaxQueuedCommands;
    status["events"] = data.Events.size();
    status["maxEvents"] = data.MaxEvents;
    status["observationSeq"] = data.ObservationSeq;
    status["lastError"] = std::string(data.LastError);
    return status;
}

static auto BuildAiControlObservation(AiControlClientData& data) -> nlohmann::json
{
    FO_STACK_TRACE_ENTRY();

    string observation_json;
    uint64_t observation_seq = 0;

    {
        scoped_lock locker(data.Locker);
        observation_json = data.ObservationJson;
        observation_seq = data.ObservationSeq;
    }

    nlohmann::json result;
    result["observationSeq"] = observation_seq;

    try {
        result["observation"] = nlohmann::json::parse(std::string(observation_json));
    }
    catch (const std::exception& ex) {
        result["observation"] = nlohmann::json::object();
        result["observationParseError"] = ex.what();
        result["observationText"] = std::string(observation_json);
    }

    return result;
}

static auto BuildAiControlEvents(AiControlClientData& data, uint64_t after_seq, size_t limit) -> nlohmann::json
{
    FO_STACK_TRACE_ENTRY();

    vector<AiControlEvent> events;
    uint64_t latest_seq = 0;

    {
        scoped_lock locker(data.Locker);
        latest_seq = data.NextEventSeq;

        for (const AiControlEvent& event : data.Events) {
            if (event.Seq <= after_seq) {
                continue;
            }

            events.emplace_back(event);

            if (events.size() >= limit) {
                break;
            }
        }
    }

    nlohmann::json result;
    result["latestSeq"] = latest_seq;
    result["events"] = nlohmann::json::array();

    for (const AiControlEvent& event : events) {
        nlohmann::json event_json;
        event_json["seq"] = event.Seq;

        try {
            event_json["event"] = nlohmann::json::parse(std::string(event.Json));
        }
        catch (const std::exception& ex) {
            event_json["event"] = nlohmann::json::object();
            event_json["parseError"] = ex.what();
            event_json["text"] = std::string(event.Json);
        }

        result["events"].push_back(std::move(event_json));
    }

    return result;
}

static auto JsonDumpToString(const nlohmann::json& value) -> string
{
    FO_STACK_TRACE_ENTRY();

    const std::string dumped = value.dump();
    return string(dumped.c_str());
}

static auto GetJsonString(const nlohmann::json& object, string_view name, string_view def_value) -> string
{
    FO_STACK_TRACE_ENTRY();

    const std::string key(name);

    if (!object.contains(key)) {
        return string(def_value);
    }

    const nlohmann::json& value = object[key];

    if (value.is_string()) {
        const std::string str = value.get<std::string>();
        return string(str.c_str());
    }
    if (value.is_number_integer()) {
        return strex("{}", value.get<int64_t>()).str();
    }
    if (value.is_boolean()) {
        return value.get<bool>() ? "true" : "false";
    }

    return string(def_value);
}

static auto GetJsonBool(const nlohmann::json& object, string_view name, bool def_value) -> bool
{
    FO_STACK_TRACE_ENTRY();

    const std::string key(name);

    if (!object.contains(key)) {
        return def_value;
    }

    const nlohmann::json& value = object[key];

    if (value.is_boolean()) {
        return value.get<bool>();
    }
    if (value.is_number_integer()) {
        return value.get<int64_t>() != 0;
    }
    if (value.is_string()) {
        return strvex(string(value.get<std::string>().c_str())).to_bool();
    }

    return def_value;
}

static auto GetJsonInt32(const nlohmann::json& object, string_view name, int32_t def_value) -> int32_t
{
    FO_STACK_TRACE_ENTRY();

    const std::string key(name);

    if (!object.contains(key)) {
        return def_value;
    }

    const nlohmann::json& value = object[key];

    if (value.is_number_integer()) {
        return numeric_cast<int32_t>(value.get<int64_t>());
    }
    if (value.is_string()) {
        return numeric_cast<int32_t>(strvex(string(value.get<std::string>().c_str())).to_int64());
    }

    return def_value;
}

static auto GetJsonUInt64(const nlohmann::json& object, string_view name, uint64_t def_value) -> uint64_t
{
    FO_STACK_TRACE_ENTRY();

    const std::string key(name);

    if (!object.contains(key)) {
        return def_value;
    }

    const nlohmann::json& value = object[key];

    if (value.is_number_unsigned()) {
        return value.get<uint64_t>();
    }
    if (value.is_number_integer()) {
        return numeric_cast<uint64_t>(std::max(value.get<int64_t>(), int64_t {}));
    }
    if (value.is_string()) {
        return numeric_cast<uint64_t>(std::max(strvex(string(value.get<std::string>().c_str())).to_int64(), int64_t {}));
    }

    return def_value;
}

static auto GetJsonIdent(const nlohmann::json& object, string_view name) -> ident_t
{
    FO_STACK_TRACE_ENTRY();

    const std::string key(name);

    if (!object.contains(key)) {
        return ident_t {};
    }

    const nlohmann::json& value = object[key];

    if (value.is_number_integer()) {
        return ident_t {value.get<int64_t>()};
    }
    if (value.is_string()) {
        return ident_t {strvex(string(value.get<std::string>().c_str())).to_int64()};
    }

    return ident_t {};
}

static void PushAiControlEvent(AiControlClientData& data, string_view event_json)
{
    FO_STACK_TRACE_ENTRY();

    scoped_lock locker(data.Locker);

    data.NextEventSeq++;
    data.Events.emplace_back(AiControlEvent {data.NextEventSeq, event_json.empty() ? "{}" : string(event_json)});

    while (data.Events.size() > data.MaxEvents) {
        data.Events.pop_front();
    }
}

static void RegisterAiControlLogCallback(AiControlClientData& data)
{
    FO_STACK_TRACE_ENTRY();

    data.LogCallbackKey = string(strex("AiControlLog.{}", data.Port).str());

    SetLogCallback(data.LogCallbackKey, [&data](LogType type, string_view message, const CatchedStackTraceData* st) {
        if (!data.Running.load(std::memory_order_acquire) || data.StopRequested.load(std::memory_order_acquire)) {
            return;
        }

        if (std::optional<string> event = TryBuildAiControlLogExceptionEvent(type, message, st); event.has_value()) {
            PushAiControlEvent(data, *event);
        }
    });
}

static void UnregisterAiControlLogCallback(AiControlClientData& data) noexcept
{
    FO_NO_STACK_TRACE_ENTRY();

    try {
        if (!data.LogCallbackKey.empty()) {
            SetLogCallback(data.LogCallbackKey, {});
            data.LogCallbackKey.clear();
        }
    }
    catch (...) {
        BreakIntoDebugger();
    }
}

static auto TryBuildAiControlLogExceptionEvent(LogType type, string_view message, const CatchedStackTraceData* st) -> std::optional<string>
{
    FO_STACK_TRACE_ENTRY();

    const string category = ClassifyAiControlLogException(type, message);
    if (category.empty()) {
        return std::nullopt;
    }

    nlohmann::json event;
    event["type"] = "runtime_exception";
    event["source"] = "engine_log";
    event["level"] = string(LogTypeToString(type));
    event["category"] = category;
    event["message"] = TrimAiControlLogMessage(message);
    event["raw"] = string(message);
    event["hasStackTrace"] = st != nullptr;

    return JsonDumpToString(event);
}

static auto ClassifyAiControlLogException(LogType type, string_view message) -> string
{
    FO_STACK_TRACE_ENTRY();

    if (ContainsCaseInsensitive(message, "ScriptException") || ContainsCaseInsensitive(message, "Script exception")) {
        return "script_exception";
    }
    if (ContainsCaseInsensitive(message, "assert") || ContainsCaseInsensitive(message, "verification")) {
        return "assertion";
    }
    if (ContainsCaseInsensitive(message, "fatal") || ContainsCaseInsensitive(message, "crash")) {
        return "fatal";
    }
    if (ContainsCaseInsensitive(message, "exception")) {
        return "exception";
    }
    if (type == LogType::Error || ContainsCaseInsensitive(message, "error :")) {
        return "error";
    }

    return {};
}

static auto LogTypeToString(LogType type) noexcept -> string_view
{
    FO_NO_STACK_TRACE_ENTRY();

    switch (type) {
    case LogType::Info:
        return "info";
    case LogType::InfoSection:
        return "info_section";
    case LogType::Warning:
        return "warning";
    case LogType::Error:
        return "error";
    default:
        break;
    }

    return "unknown";
}

static auto TrimAiControlLogMessage(string_view message) -> string
{
    FO_STACK_TRACE_ENTRY();

    size_t begin = 0;
    size_t end = message.length();

    while (begin < end && std::isspace(static_cast<unsigned char>(message[begin])) != 0) {
        begin++;
    }
    while (end > begin && std::isspace(static_cast<unsigned char>(message[end - 1])) != 0) {
        end--;
    }

    return string(message.substr(begin, end - begin));
}

static bool ContainsCaseInsensitive(string_view text, string_view needle) noexcept
{
    FO_NO_STACK_TRACE_ENTRY();

    if (needle.empty()) {
        return true;
    }
    if (needle.length() > text.length()) {
        return false;
    }

    for (size_t i = 0; i <= text.length() - needle.length(); i++) {
        bool match = true;

        for (size_t j = 0; j < needle.length(); j++) {
            const int32_t left = std::tolower(static_cast<unsigned char>(text[i + j]));
            const int32_t right = std::tolower(static_cast<unsigned char>(needle[j]));

            if (left != right) {
                match = false;
                break;
            }
        }

        if (match) {
            return true;
        }
    }

    return false;
}

#else

bool FO_NAMESPACE Client_Game_AiControlStart(ClientEngine* client, bool enabled, string_view host, int32_t port, string_view token, int32_t maxQueuedCommands, int32_t maxEvents)
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(client, enabled, host, port, token, maxQueuedCommands, maxEvents);
    return false;
}

void FO_NAMESPACE Client_Game_AiControlStop(ClientEngine* client)
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(client);
}

bool FO_NAMESPACE Client_Game_AiControlIsRunning(ClientEngine* client)
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(client);
    return false;
}

bool FO_NAMESPACE Client_Game_AiControlPullCommand(ClientEngine* client, uint32_t& commandSeq, string& type, ident_t& targetId, ident_t& itemId, ident_t& auxId, int32_t& hexX, int32_t& hexY, int32_t& screenX, int32_t& screenY, int32_t& intArg, string& stringArg, bool& append)
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(client);
    commandSeq = 0;
    type = "";
    targetId = ident_t {};
    itemId = ident_t {};
    auxId = ident_t {};
    hexX = 0;
    hexY = 0;
    screenX = 0;
    screenY = 0;
    intArg = 0;
    stringArg = "";
    append = false;
    return false;
}

void FO_NAMESPACE Client_Game_AiControlSetObservation(ClientEngine* client, string_view observationJson)
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(client, observationJson);
}

void FO_NAMESPACE Client_Game_AiControlPushEvent(ClientEngine* client, string_view eventJson)
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(client, eventJson);
}

void FO_NAMESPACE Client_Game_AiControlCompleteCommand(ClientEngine* client, uint32_t commandSeq, bool success, string_view message)
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(client, commandSeq, success, message);
}

string FO_NAMESPACE Client_Game_AiControlGetStatus(ClientEngine* client)
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(client);
    return "{}";
}

ident_t FO_NAMESPACE Client_Game_AiControlGetEntityId(ClientEngine* client, ClientEntity* entity)
{
    FO_STACK_TRACE_ENTRY();

    ignore_unused(client, entity);
    return ident_t {};
}

#endif
