# Client console commands

Enter commands in the game chat console with a leading `~`:

- `~myinfo`: controlled character name, IdCritter, map id, hex and command access.
- `~additemself bottle_caps 100`: add units using the game item-stack helpers.
- `~prop 123 Strength 10`: set a mutable scalar property of a loaded critter.
  Commas also separate arguments: `~prop 123, Strength, 10`.

Property names are resolved through `CritterProperty`; values are converted by
`SetAsAny`, which rejects disabled, immutable and non-scalar properties. Arrays,
dictionaries and strings are not supported by this command. Unknown prototypes,
critters and malformed arguments produce a console message. Item counts must be
1..1000000; non-stackable additions are capped at 100 instances per command.

`myinfo` is available to everyone. The server authorizes mutations using:

```ini
ConsoleCommands.AllowEveryone = False
ConsoleCommands.AdminNames = AdminAccount;AnotherAdmin
```

Account names are matched exactly, not character names. The current base config
sets `AllowEveryone = True` at the owner's request; set it to False to restrict
mutations to the account list. Successful mutation commands are logged with the
account name. Client-side changes cannot bypass the server authorization check.

Implementation: `Scripts/ConsoleCommands.fos`, called by `Messaging.fos`.
No engine modifications are required. Legacy references: `Access.cpp` command
names and `Server.cpp` handlers in `C:/work/foclassic/Source`.

Manual checks after baking: myinfo; valid/unknown prototype; stacked and separate
items; zero/negative/oversized count; existing/missing critter; mutable/unknown/
read-only property; denied mutation with AllowEveryone=False and no listed name;
allowed mutation for a listed account. Ordinary chat must continue to work.
