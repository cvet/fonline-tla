#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


CODE_KEYS = {'GlobalScope', 'ClassFields', 'DynamicText', 'Text', 'GridSize'}
CALLBACK_METHODS = [
    ('OnInit', 'void OnInit() override'),
    ('OnShow', 'void OnShow(dict<string, any> params) override'),
    ('OnHide', 'void OnHide() override'),
    ('OnAppear', 'void OnAppear() override'),
    ('OnDisappear', 'void OnDisappear() override'),
    ('OnDraw', 'void OnDraw() override'),
    ('OnPostDraw', 'void OnPostDraw() override'),
    ('OnMove', 'void OnMove(int deltaX, int deltaY) override'),
    ('OnMouseDown', 'void OnMouseDown(MouseButton button) override'),
    ('OnMouseUp', 'void OnMouseUp(MouseButton button, bool lost) override'),
    ('OnMousePressed', 'void OnMousePressed(MouseButton button) override'),
    ('OnLMousePressed', 'void OnLMousePressed() override'),
    ('OnRMousePressed', 'void OnRMousePressed() override'),
    ('OnMouseClick', 'void OnMouseClick(MouseButton button) override'),
    ('OnLMouseClick', 'void OnLMouseClick() override'),
    ('OnRMouseClick', 'void OnRMouseClick() override'),
    ('OnMouseMove', 'void OnMouseMove() override'),
    ('OnGlobalMouseDown', 'void OnGlobalMouseDown(MouseButton button) override'),
    ('OnGlobalMouseUp', 'void OnGlobalMouseUp(MouseButton button) override'),
    ('OnGlobalMousePressed', 'void OnGlobalMousePressed(MouseButton button) override'),
    ('OnGlobalMouseClick', 'void OnGlobalMouseClick(MouseButton button) override'),
    ('OnGlobalMouseMove', 'void OnGlobalMouseMove() override'),
    ('OnInput', 'void OnInput(KeyCode key, string text) override'),
    ('OnGlobalInput', 'void OnGlobalInput(KeyCode key, string text) override'),
    ('OnActiveChanged', 'void OnActiveChanged() override'),
    ('OnFocusChanged', 'void OnFocusChanged() override'),
    ('OnHoverChanged', 'void OnHoverChanged() override'),
    ('OnDragChanged', 'void OnDragChanged() override'),
    ('OnResizeGrid', 'void OnResizeGrid(Gui::Object cell, int cellIndex) override'),
    ('OnDrawItem', 'void OnDrawItem(Item item, Gui::Object cell, int cellIndex) override'),
]


class TerminalProgress:
    def __init__(self, prefix: str) -> None:
        self._prefix = prefix
        self._last_len = 0

    def update(self, message: str) -> None:
        line = f'[{self._prefix}] {message}'
        padding = ' ' * max(0, self._last_len - len(line))
        sys.stdout.write('\r' + line + padding)
        sys.stdout.flush()
        self._last_len = len(line)

    def clear(self) -> None:
        if self._last_len == 0:
            return

        sys.stdout.write('\r' + ' ' * self._last_len + '\r')
        sys.stdout.flush()
        self._last_len = 0

    def finish(self, message: str) -> None:
        self.clear()
        print(f'[{self._prefix}] {message}', flush=True)


def log_progress(message: str) -> None:
    print(f'[GuiGenerator] {message}', flush=True)


def read_text_strip_bom(path: Path) -> str:
    return path.read_bytes().decode('utf-8-sig')


def detect_line_ending(content: str) -> str:
    return '\r\n' if '\r\n' in content else '\n'


def normalize_line_endings(content: str, line_ending: str) -> str:
    return content.replace('\r\n', '\n').replace('\r', '\n').replace('\n', line_ending)


def write_text_utf8(path: Path, content: str) -> None:
    path.write_bytes(content.encode('utf-8'))


def discover_clang_format(project_root: Path) -> str:
    bundled = project_root / 'Tools' / 'Formatter' / 'clang-format-20.exe'
    if sys.platform == 'win32' and bundled.is_file():
        return str(bundled)

    for executable in ('clang-format-20', 'clang-format'):
        path = shutil.which(executable)
        if path:
            return path

    raise SystemExit('clang-format not found')


def parse_cfg(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in read_text_strip_bom(path).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or '=' not in stripped:
            continue
        key, value = stripped.split('=', 1)
        values[key.strip()] = value.strip()
    return values


def resolve_path(base_dir: Path, raw_value: str | None, fallback: Path) -> Path:
    if not raw_value:
        return fallback
    return (base_dir / raw_value.strip()).resolve()


def decode_fogui(content: str) -> str:
    if not content.startswith('// FOGUI V2'):
        return content

    lines = content.replace('\r\n', '\n').split('\n')
    result: list[str] = []
    index = 1
    while index < len(lines):
        line = lines[index]

        if index == len(lines) - 1 and line == '':
            break
        if not line.startswith('// '):
            raise ValueError(f'Invalid code format at line {index + 1}')

        is_code_line = False
        colon_index = line.find(':')
        if colon_index != -1 and len(line) == colon_index + 1:
            key_start = line.find('"')
            key_end = line.find('"', key_start + 1)
            key = line[key_start + 1:key_end]

            if key.startswith('On') or key in CODE_KEYS:
                result.append(line[3:])
                result.append(' "')
                index += 1

                idents = 3
                if key == 'GlobalScope':
                    idents = 1
                elif key == 'ClassFields':
                    idents = 2

                for depth in range(idents):
                    expected = ' ' * (depth * 4) + '{'
                    if index >= len(lines) or lines[index] != expected:
                        raise ValueError(f'Invalid code format at line {index + 1}')
                    index += 1

                end_line = ' ' * ((idents - 1) * 4) + '}'
                first_line = True
                while index < len(lines) and lines[index] != end_line:
                    if first_line:
                        first_line = False
                    else:
                        result.append('\\r\\n')

                    if len(lines[index]) >= idents * 4:
                        result.append(lines[index][idents * 4:].replace('"', '\\"'))
                    index += 1

                for depth in range(idents - 1, -1, -1):
                    expected = ' ' * (depth * 4) + '}'
                    if index >= len(lines) or lines[index] != expected:
                        raise ValueError(f'Invalid code format at line {index + 1}')
                    index += 1

                result.append('",')
                index -= 1
                is_code_line = True

        if not is_code_line:
            result.append(line[3:])
            result.append('\n')

        index += 1

    return ''.join(result)


def parse_gui_file(path: Path) -> dict:
    return json.loads(decode_fogui(read_text_strip_bom(path)))


def parse_scheme(path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for line in read_text_strip_bom(path).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        parts = stripped.split()
        if len(parts) != 2:
            raise ValueError(f'Invalid GUI scheme row: {line}')
        entries.append((parts[0], parts[1]))
    return entries


def parse_pair(value: str | None) -> tuple[int, int] | None:
    if not value:
        return None
    left, right = (part.strip() for part in value.split(',', 1))
    return int(left), int(right)


def is_non_empty(value: object) -> bool:
    return isinstance(value, str) and value != ''


def append_code(lines: list[str], code: str, indent: str) -> None:
    normalized = normalize_code(code)
    for line in normalized.replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        lines.append(indent + line)


def convert_anchor(value: str | None) -> str | None:
    if not value or value == 'None':
        return None
    parts = {part.strip() for part in value.split(',') if part.strip()}
    ordered_parts = ['Left', 'Right', 'Top', 'Bottom']
    mapped = [f'AnchorStyle::{part}' for part in ordered_parts if part in parts]
    return ' | '.join(mapped) if mapped else None


def convert_dock(value: str | None) -> str | None:
    if not value or value == 'None':
        return None
    return f'DockStyle::{value}'


def convert_layout(value: str | None) -> str | None:
    if not value or value == 'None':
        return None
    return f'SpriteLayout::{value}'


def make_image_expr(value: str) -> str:
    stripped = value.strip()
    if '/' in stripped or '\\' in stripped:
        escaped = stripped.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    return stripped


def normalize_array_initializer(value: str) -> str:
    return re.sub(r'^array<[^>]+>\s*=\s*', '', value.strip())


def normalize_code(code: str) -> str:
    normalized = code
    normalized = re.sub(r'SetDisplayedMessages\(array<[^>]+>\s*=\s*(\{.*?\})\);', r'SetDisplayedMessages(\1);', normalized)
    return normalized


def load_existing_prefixes(path: Path) -> tuple[dict[str, str], list[str]]:
    if not path.is_file():
        return {}, []

    content = read_text_strip_bom(path)
    screen_prefixes = dict(re.findall(r'Gui::RegisterScreen\(GuiScreen::(\w+), GuiScreens::(\w+)::CreateScreen\);', content))
    custom_prefixes = re.findall(r'// Custom hierarchy: GuiScreens::(\w+)::CreateHierarchy', content)
    return screen_prefixes, custom_prefixes


def append_image_call(lines: list[str], indent: str, method: str, image: str | None, layout: str | None) -> None:
    if not image:
        return
    image_expr = make_image_expr(image)
    if layout and layout != 'SpriteLayout::None':
        lines.append(f'{indent}{method}({image_expr}, {layout});')
    else:
        lines.append(f'{indent}{method}({image_expr});')


def emit_on_construct(lines: list[str], obj: dict, is_root: bool) -> None:
    indent = '        '
    obj_type = obj['$type']

    if is_root and obj_type == 'Screen':
        if obj.get('IsModal'):
            lines.append(f'{indent}SetModal(true);')
        if obj.get('IsMultiinstance'):
            lines.append(f'{indent}SetMultiinstance(true);')
        if obj.get('IsCloseOnMiss'):
            lines.append(f'{indent}SetCloseOnMiss(true);')
        if is_non_empty(obj.get('AvailableCursors')):
            lines.append(f'{indent}SetAvailableCursors({obj["AvailableCursors"]});')
        if obj.get('IsCanMove'):
            ignore_borders = str(bool(obj.get('IsMoveIgnoreBorders'))).lower()
            lines.append(f'{indent}SetCanMove(true, {ignore_borders});')

    if not obj.get('Active', True):
        lines.append(f'{indent}SetActive(false);')

    position = parse_pair(obj.get('Position'))
    if position and position != (0, 0):
        lines.append(f'{indent}SetPosition({position[0]}, {position[1]});')

    size = parse_pair(obj.get('Size'))
    if size and size != (0, 0):
        lines.append(f'{indent}SetSize({size[0]}, {size[1]});')

    anchor = convert_anchor(obj.get('Anchor'))
    if anchor:
        lines.append(f'{indent}SetAnchor(AnchorStyle({anchor}));')

    dock = convert_dock(obj.get('Dock'))
    if dock:
        lines.append(f'{indent}SetDock({dock});')

    if obj.get('IsDraggable'):
        lines.append(f'{indent}SetDraggable(true);')
    if obj.get('IsNotHittable'):
        lines.append(f'{indent}SetNotHittable(true);')
    if obj.get('CheckTransparentOnHit'):
        lines.append(f'{indent}SetCheckTransparentOnHit(true);')
    if obj.get('FocusGroup'):
        lines.append(f'{indent}SetFocusGroup(true);')

    if obj_type in {'Screen', 'Panel', 'Button', 'CheckBox', 'RadioButton', 'Grid', 'ItemView'}:
        append_image_call(lines, indent, 'SetBackgroundImage', obj.get('BackgroundImage'), convert_layout(obj.get('BackgroundImageLayout')))
        if obj.get('CropContent'):
            lines.append(f'{indent}SetCropContent(true);')
        if obj.get('IsVerticalScroll') or obj.get('IsHorizontalScroll'):
            vertical = str(bool(obj.get('IsVerticalScroll'))).lower()
            horizontal = str(bool(obj.get('IsHorizontalScroll'))).lower()
            lines.append(f'{indent}SetAutoScroll({vertical}, {horizontal});')

    if obj_type in {'Button', 'CheckBox', 'RadioButton'}:
        if obj.get('IsDisabled'):
            lines.append(f'{indent}SetCondition(false);')
        append_image_call(lines, indent, 'SetPressedImage', obj.get('PressedImage'), convert_layout(obj.get('PressedImageLayout')))
        append_image_call(lines, indent, 'SetHoverImage', obj.get('HoverImage'), convert_layout(obj.get('HoverImageLayout')))
        append_image_call(lines, indent, 'SetDisabledImage', obj.get('DisabledImage'), convert_layout(obj.get('DisabledImageLayout')))

    if obj_type in {'CheckBox', 'RadioButton'} and is_non_empty(obj.get('IsChecked')):
        lines.append(f'{indent}SetChecked({obj["IsChecked"]});')

    if obj_type in {'Text', 'TextInput', 'MessageBox', 'Console'}:
        if is_non_empty(obj.get('Text')):
            lines.append(f'{indent}SetText({obj["Text"]});')
        if is_non_empty(obj.get('Font')):
            lines.append(f'{indent}SetTextFont({obj["Font"]});')

        text_flags: list[str] = []
        if obj.get('HorisontalAlignment') == 'Center':
            text_flags.append('FT_CENTERX')
        if obj.get('VerticalAlignment') == 'Center':
            text_flags.append('FT_CENTERY')
        if obj.get('HorisontalAlignment') == 'Far':
            text_flags.append('FT_CENTERR')
        if obj.get('VerticalAlignment') == 'Far':
            text_flags.append('FT_BOTTOM')
        if obj.get('DrawFromBottom'):
            text_flags.append('FT_UPPER')
        if obj.get('NoColorize'):
            text_flags.append('FT_NO_COLORIZE')
        if obj.get('Align'):
            text_flags.append('FT_ALIGN')
        if obj.get('Bordered'):
            text_flags.append('FT_BORDERED')
        if text_flags:
            joined_flags = ' | '.join(text_flags)
            lines.append(f'{indent}SetTextFlags({joined_flags});')

        if is_non_empty(obj.get('NormalColor')):
            lines.append(f'{indent}SetTextColor({obj["NormalColor"]});')
        if is_non_empty(obj.get('FocusedColor')):
            lines.append(f'{indent}SetTextFocusedColor({obj["FocusedColor"]});')

    if obj_type in {'TextInput', 'Console'}:
        if is_non_empty(obj.get('InputLength')):
            lines.append(f'{indent}SetInputLength({obj["InputLength"]});')
        if obj.get('Password'):
            lines.append(f'{indent}SetInputPassword("#");')

    if obj_type == 'MessageBox':
        if is_non_empty(obj.get('InvertMessages')):
            lines.append(f'{indent}SetInvertMessages({obj["InvertMessages"]});')
        if is_non_empty(obj.get('DisplayedMessages')):
                displayed_messages = normalize_array_initializer(obj['DisplayedMessages'])
                lines.append(f'{indent}SetDisplayedMessages({displayed_messages});')

    if obj_type == 'Console':
        if obj.get('DisableDeactivation'):
            lines.append(f'{indent}SetDisableDeactivation(true);')
        if is_non_empty(obj.get('HistoryStorageName')):
            lines.append(f'{indent}SetHistoryStorage({obj["HistoryStorageName"]});')
        if is_non_empty(obj.get('HistoryMaxLength')):
            lines.append(f'{indent}SetHistoryMaxLength({obj["HistoryMaxLength"]});')

    if obj_type in {'Grid', 'ItemView'}:
        if is_non_empty(obj.get('CellPrototype')):
            lines.append(f'{indent}SetCellPrototype({obj["CellPrototype"]});')
        if is_non_empty(obj.get('GridSize')):
            lines.append(f'{indent}SetGridSize({obj["GridSize"]});')
        if obj.get('Columns'):
            lines.append(f'{indent}SetColumns({obj["Columns"]});')
        padding = parse_pair(obj.get('Padding'))
        if padding and padding != (0, 0):
            lines.append(f'{indent}SetPadding({padding[0]}, {padding[1]});')

    if obj_type == 'ItemView':
        if is_non_empty(obj.get('UserData')):
            lines.append(f'{indent}SetUserData({obj["UserData"]});')
        if is_non_empty(obj.get('UserDataExt')):
            lines.append(f'{indent}SetUserDataExt({obj["UserDataExt"]});')
        if obj.get('UseSorting'):
            lines.append(f'{indent}SetUseSorting(true);')


def emit_class(lines: list[str], obj: dict, is_root: bool) -> None:
    class_name = get_class_name(obj, is_root)

    if not is_root:
        lines.append('')

    if is_non_empty(obj.get('GlobalScope')):
        append_code(lines, obj['GlobalScope'], '')
        lines.append('')

    lines.append(f'class {class_name} : Gui::{obj["$type"]}')
    lines.append('{')

    if is_non_empty(obj.get('ClassFields')):
        append_code(lines, obj['ClassFields'], '    ')
        lines.append('')

    lines.append('    void OnConstruct() override')
    lines.append('    {')
    emit_on_construct(lines, obj, is_root)
    lines.append('    }')

    if obj['$type'] in {'Text', 'TextInput', 'MessageBox', 'Console'} and is_non_empty(obj.get('Text')):
        lines.append('')
        lines.append('    void OnRefreshText() override')
        lines.append('    {')
        lines.append(f'        SetText({obj["Text"]});')
        lines.append('    }')

    for callback_key, signature in CALLBACK_METHODS:
        if is_non_empty(obj.get(callback_key)):
            lines.append('')
            lines.append(f'    {signature}')
            lines.append('    {')
            append_code(lines, obj[callback_key], '        ')
            lines.append('    }')

    if obj['$type'] in {'CheckBox', 'RadioButton'} and is_non_empty(obj.get('OnCheckedChanged')):
        lines.append('')
        lines.append('    void OnCheckedChanged() override')
        lines.append('    {')
        append_code(lines, obj['OnCheckedChanged'], '        ')
        lines.append('    }')

    if obj['$type'] == 'ItemView' and is_non_empty(obj.get('OnGetItems')):
        lines.append('')
        lines.append('    Item[] OnGetItems() override')
        lines.append('    {')
        append_code(lines, obj['OnGetItems'], '        ')
        lines.append('    }')

    if obj['$type'] == 'ItemView' and is_non_empty(obj.get('OnCheckItem')):
        lines.append('')
        lines.append('    int OnCheckItem(Item item) override')
        lines.append('    {')
        append_code(lines, obj['OnCheckItem'], '        ')
        lines.append('    }')

    if obj['$type'] in {'Text', 'TextInput', 'MessageBox', 'Console'} and is_non_empty(obj.get('DynamicText')):
        lines.append('')
        lines.append('    string get_Text() override')
        lines.append('    {')
        append_code(lines, obj['DynamicText'], '        ')
        lines.append('    }')

    lines.append('};')


def walk_objects(obj: dict):
    yield obj
    for child in obj.get('Children') or []:
        yield from walk_objects(child)


def count_objects(obj: dict) -> int:
    return sum(1 for _ in walk_objects(obj))


def get_class_name(obj: dict, is_root: bool) -> str:
    return obj['Name']


def emit_hierarchy(lines: list[str], obj: dict) -> None:
    class_name = get_class_name(obj, obj.get('$is_root', False))
    lines.append('')
    lines.append(f'{class_name} Create{class_name}Hierarchy(Gui::Object parent)')
    lines.append('{')
    lines.append(f'    {class_name} obj = {class_name}();')
    for child in obj.get('Children') or []:
        child_class_name = get_class_name(child, False)
        lines.append(f'    Create{child_class_name}Hierarchy(obj);')
    lines.append('    obj.Init(parent);')
    lines.append('    return obj;')
    lines.append('}')

    for child in obj.get('Children') or []:
        emit_hierarchy(lines, child)


def emit_namespace(namespace_name: str, root: dict) -> list[str]:
    lines = [f'namespace {namespace_name}', '{']
    root['$is_root'] = True
    for obj in walk_objects(root):
        emit_class(lines, obj, obj is root)
    emit_hierarchy(lines, root)
    lines.append('')
    root_class_name = get_class_name(root, True)
    if root['$type'] == 'Screen':
        lines.append('Gui::Screen CreateScreen()')
        lines.append('{')
        lines.append(f'    return Create{root_class_name}Hierarchy(null);')
        lines.append('}')
    else:
        lines.append(f'{root_class_name} CreateHierarchy(Gui::Object parent)')
        lines.append('{')
        lines.append(f'    return Create{root_class_name}Hierarchy(parent);')
        lines.append('}')
    lines.append('}')
    return lines


def generate_script(project_root: Path, gui_path: Path, scheme_path: Path) -> str:
    entries = parse_scheme(scheme_path)
    log_progress(f'Loaded scheme {scheme_path.name} with {len(entries)} entries')

    init_lines = ['void InitializeScreens()', '{']
    namespace_blocks: list[str] = []
    screen_prefixes, custom_prefixes = load_existing_prefixes(project_root / 'Scripts' / 'GuiScreens.fos')
    custom_index = 0
    progress = TerminalProgress('GuiGenerator')

    for index, (screen_name, gui_file_name) in enumerate(entries, start=1):
        gui_file_path = gui_path / gui_file_name
        root = parse_gui_file(gui_file_path)
        default_prefix = Path(gui_file_name).stem
        if screen_name != 'CUSTOM':
            namespace_name = default_prefix
        else:
            namespace_name = custom_prefixes[custom_index] if custom_index < len(custom_prefixes) else default_prefix
            custom_index += 1

        root_name = root.get('Name', '<unnamed>')
        object_count = count_objects(root)
        progress.update(
            f'[{index}/{len(entries)}] {screen_name} <- {gui_file_name} '
            f'(namespace {namespace_name}, root {root_name}, objects {object_count})'
        )

        if screen_name != 'CUSTOM':
            init_lines.append(f'    ///@ Enum GuiScreen {screen_name}')
            init_lines.append(f'    Gui::RegisterScreen(GuiScreen::{screen_name}, GuiScreens::{namespace_name}::CreateScreen);')
        else:
            init_lines.append(f'    // Custom hierarchy: GuiScreens::{namespace_name}::CreateHierarchy')

        namespace_blocks.append('\n'.join(emit_namespace(namespace_name, root)))

    init_lines.append('}')
    progress.finish(f'Generated {len(entries)} screen definition(s)')

    return '\n'.join([
        'namespace GuiScreens',
        '{',
        '',
        '#if CLIENT',
        '',
        f'// GUI scheme name: {scheme_path.stem}',
        '',
        '\n'.join(init_lines),
        '',
        '\n\n'.join(namespace_blocks),
        '',
        '#endif',
        '',
        '}',
        '',
    ])


def format_output(path: Path, project_root: Path) -> None:
    clang_format = discover_clang_format(project_root)
    log_progress(f'Formatting {path.name} with {Path(clang_format).name}')
    subprocess.check_call([clang_format, '-i', str(path)])


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Generate Scripts/GuiScreens.fos from Gui/*.fogui')
    parser.add_argument('--project-root', type=Path)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--scheme', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--no-format', action='store_true')
    return parser


def main() -> None:
    args = create_parser().parse_args()

    tool_dir = Path(__file__).resolve().parent
    project_root = args.project_root.resolve() if args.project_root else tool_dir.parents[1]
    config_path = args.config.resolve() if args.config else tool_dir / 'InterfaceEditor.cfg'

    config = parse_cfg(config_path)
    gui_path = resolve_path(config_path.parent, config.get('GuiPath'), project_root / 'Gui')
    output_dir = resolve_path(config_path.parent, config.get('GuiOutputPath'), project_root / 'Scripts')
    scheme_path = args.scheme.resolve() if args.scheme else gui_path / 'Default.foguischeme'
    output_path = args.output.resolve() if args.output else output_dir / 'GuiScreens.fos'

    log_progress(f'Project root: {project_root}')
    log_progress(f'GUI path: {gui_path}')
    log_progress(f'Output: {output_path}')

    output_path.parent.mkdir(parents=True, exist_ok=True)
    log_progress('Generating GuiScreens script')
    line_ending = '\n'
    if output_path.is_file():
        line_ending = detect_line_ending(read_text_strip_bom(output_path))

    generated = normalize_line_endings(generate_script(project_root, gui_path, scheme_path), line_ending)
    write_text_utf8(output_path, generated)
    if not args.no_format:
        format_output(output_path, project_root)

    try:
        rel_path = output_path.relative_to(project_root).as_posix()
    except ValueError:
        rel_path = str(output_path)

    log_progress(f'Wrote {rel_path}')


if __name__ == '__main__':
    main()