# HMM Supported Games

The game catalog for **Hyura Mod Manager (HMM)**.

HMM reads these lists directly from this repository, so adding a game here makes it
available in the app without a new HMM release. Changes go live as soon as they are
merged into `main`.

HMM builds are published on the
[Hyura-Mod-Manager releases page](https://github.com/TaylorHyura/Hyura-Mod-Manager/releases).
The application source is not public yet; this repository contains only the catalog.

**Contributions are welcome.** Anyone can propose a change by opening a pull request.
Every pull request is reviewed and merged by the repository owner.

- [The two lists](#the-two-lists)
- [Adding a game](#adding-a-game)
- [Entry format](#entry-format)
- [Mod directories](#mod-directories)
- [Dependencies](#dependencies)
- [Covers](#covers)
- [Formatting rules](#formatting-rules)
- [Before you open a pull request](#before-you-open-a-pull-request)
- [Review and approval](#review-and-approval)
- [Reporting a problem](#reporting-a-problem)
- [Attribution](#attribution)

## The two lists

| File | Purpose | Who edits it |
| --- | --- | --- |
| [`lists/main_list.json`](lists/main_list.json) | Officially supported games, curated by the HMM maintainer. | Maintainer only |
| [`lists/community_list.json`](lists/community_list.json) | Community-supported games. This is the target for most pull requests. | Anyone, via pull request |

HMM loads both lists and groups them as **Officially Supported** and **Community
Supported** in the Browse screen. Both tiers are fully usable; the split only shows
where a game came from.

A game ID must be unique across both files. If the same ID appears twice, HMM keeps
the first entry it reads (the official list) and ignores the later one.

The app fetches the lists from:

- `https://raw.githubusercontent.com/TaylorHyura/HMM-Supported-Games/main/lists/main_list.json`
- `https://raw.githubusercontent.com/TaylorHyura/HMM-Supported-Games/main/lists/community_list.json`

Once a user adds a game, HMM stores a copy under `SupportedGames/<game-id>.json` and
updates it when the catalog entry changes.

## Adding a game

1. Fork this repository.
2. Add one entry to `lists/community_list.json`. Append it at the end of the array.
3. Fill in the fields described below and check the entry against the
   [formatting rules](#formatting-rules).
4. Open a pull request. The [pull request template](.github/PULL_REQUEST_TEMPLATE.md)
   lists the checks the owner will make.
5. The owner reviews the entry, may ask for changes, and merges it. Do not merge your
   own pull request or push directly to `main`.

New games are normally added to the community list first. The maintainer can promote a
well-tested entry to the official list later.

### Minimal example

A game that uses an existing engine handler and only needs dependency support:

```json
{
    "ID": "residentevil42023",
    "Name": "Resident Evil 4",
    "Engine": "REEngine",
    "CoverURL": "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/2050650/library_600x900.jpg",
    "ModDirectories": [],
    "Source": "Nexus"
}
```

### Full example

An Unreal Engine game with mod directories and one dependency:

```json
{
    "ID": "palworld",
    "Name": "Palworld",
    "Engine": "UnrealEngine",
    "CoverURL": "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/1623730/f85c38b444047c686d44eea5f649c9ae761fd06a/library_capsule.jpg",
    "ModDirectories": [
        {
            "Type": "pak",
            "Directory": "Pal\\Content\\Paks\\~Mods"
        },
        {
            "Type": "logicpak",
            "Directory": "Pal\\Content\\Paks\\LogicMods"
        },
        {
            "Type": "lua",
            "Directory": "Pal\\Binaries\\Win64\\ue4ss\\Mods"
        }
    ],
    "Dependencies": [
        {
            "Id": "REUE4SS",
            "Name": "RE-UE4SS",
            "Variant": "UE4SS (Experimental)",
            "Description": "Lua scripting system platform, C++ Modding API, SDK generator, blueprint mod loader, live property editor and other dumping utilities for UE4/5 games.",
            "Author": "Okaetsu",
            "CoverURL": "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/1623730/57df7aed61d65c9012a11d58e812aff275b7daed/capsule_616x353_2x.jpg",
            "WebPage": "https://github.com/Okaetsu/RE-UE4SS",
            "Link": "https://github.com/Okaetsu/RE-UE4SS/releases/download/experimental-palworld/UE4SS-Palworld.zip",
            "Files": [
                {
                    "Source": "dwmapi.dll",
                    "Destination": "Pal\\Binaries\\Win64\\dwmapi.dll"
                }
            ],
            "Folders": [
                {
                    "Source": "ue4ss",
                    "Destination": "Pal\\Binaries\\Win64\\ue4ss"
                }
            ]
        }
    ],
    "Source": "Nexus"
}
```

## Entry format

Each item in a list describes one game. HMM deserializes these keys into its
`SupportedGame` model.

| Field | Required | Description |
| --- | --- | --- |
| `ID` | Yes | Stable identifier for the game. When the game has a Nexus domain, use it lowercased. HMM uses the ID for `SupportedGames/<ID>.json`, covers and Nexus URLs, so never change it after release. Use only lowercase letters, digits, `-` and `_`. |
| `Name` | Yes | Display name shown in the app. |
| `Engine` | Yes | Native handler to use, or the game's engine name for Hyura-only entries. See [supported engines](#supported-engines). |
| `CoverURL` | Strongly recommended | Direct HTTPS URL to a portrait cover image. HMM downloads and caches it. See [Covers](#covers). |
| `ModDirectories` | For Unreal Engine | Where each kind of mod file is installed. Use `[]` for engines that do not need it. |
| `Dependencies` | No | Loaders or tools the game needs, such as REFramework or UE4SS. Omit the key when there are none. |
| `Source` | Yes | Where mods for this game come from. Currently only `Nexus` is handled; use it for a game with a Nexus Mods domain. Other values are reserved. |
| `CoverPath` | Do not add | Written by HMM on the user's machine. It must not appear in the catalog. |

### Supported engines

HMM has native handlers for the engines below. A handler detects and installs that
engine's usual mod formats automatically.

| Engine value | What HMM understands |
| --- | --- |
| `UnrealEngine` | `.pak` mods, LogicMods, loose Lua and DLL mods (UE4SS-style), and overwrite/loader mods. `ModDirectories` is required. |
| `REEngine` | REFramework plugin DLLs, Fluffy-style `modinfo.ini` packages (including addons), and PAK invalidation for `natives` files. |
| `MTFramework` | `nativePC`-style archives and overwrite mods. |
| `RenderWare` | No native handler. Hyura packages still install. |

**Any engine is supported when the mod is a Hyura package.** Hyura packages use HMM's
native `hyuramod.json` manifest and are installed by the app instead of an engine
handler. They work on any engine; each component folder simply mirrors the game's
install layout. See the
[Hyura mod format](https://github.com/TaylorHyura/Hyura-Mod-Manager#hyura-mod-format)
for the manifest fields and install behavior.

`Engine` is still required. For a game whose engine has no native handler, use the
engine's name; the validator warns about values outside the table so they can be
reviewed. Only Hyura packages will install for such an entry. For the handlers above,
use the exact casing shown; the value is case-sensitive in the app.

## Mod directories

`ModDirectories` tells HMM where to place Unreal Engine mod files. Every path is
relative to the game install root and uses `\\` separators in JSON. Do not include a
drive letter, a leading slash, or the game executable.

| `Type` | Meaning | Typical value |
| --- | --- | --- |
| `pak` | Regular `.pak` mods and loose files that belong in `~Mods`. | `GameName\\Content\\Paks\\~Mods` |
| `logicpak` | Blueprint/LogicMods `.pak` files. | `GameName\\Content\\Paks\\LogicMods` |
| `lua` | UE4SS Lua mods. | `GameName\\Binaries\\Win64\\ue4ss\\Mods` |
| `hook` | Hook/overwrite files and loader DLLs, such as `dwmapi.dll`. | `GameName\\Binaries\\Win64` |

`UnrealEngine` entries must provide at least `pak`. Add `logicpak`, `lua` and `hook`
only when the game supports them and the folder exists on a normal install. Wrong
paths make mods install silently into the wrong place, so verify them against a real
game folder.

## Dependencies

A dependency is a loader or tool the game needs before mods will work. HMM shows
dependencies in the Dependencies screen and installs the selected ones on demand.

| Field | Required | Description |
| --- | --- | --- |
| `Id` | Yes | Short identifier, unique within the game. Used by the app to track the dependency. |
| `Name` | Yes | Display name. |
| `Variant` | Yes | Label for this particular build, for example `REFramework RT` or `UE4SS (Experimental)`. HMM uses it as the installed file name. |
| `Description` | Recommended | One or two sentences explaining what the dependency does. |
| `Author` | Recommended | Original author or maintainer. Defaults to `Unknown` when omitted. |
| `CoverURL` | Optional | Direct HTTPS image URL. |
| `WebPage` | Recommended | Project page, usually the GitHub repository or official site. |
| `Link` | Yes | Direct download URL for the archive. Prefer a versioned release asset or a stable `latest` asset. |
| `Files` | Optional | Files to move out of the archive: `{ "Source": "...", "Destination": "..." }`. |
| `Folders` | Optional | Folders to move out of the archive: `{ "Source": "...", "Destination": "..." }`. |
| `Config` | Optional | A config file to write: `{ "Name": "...", "Type": "...", "Content": "..." }`. HMM writes it as `<Name>.<Type>` in the mod folder. |

`Source` in `Files` and `Folders` is relative to the archive root after extraction.
`Destination` is relative to the game install root. Match the layout the dependency
author ships; do not guess a folder name.

Use a direct link to the archive, not a release page or a page that needs a browser
session. If a project publishes several builds, add one dependency entry per build and
make each `Variant` distinct.

## Covers

`CoverURL` must point directly at an image file over HTTPS. HMM downloads it and
caches it locally. A portrait image works best; Steam's `library_600x900.jpg`
is a good source:

```text
https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/<appid>/<hash>/library_600x900.jpg
```

Avoid:

- Nexus Mods page URLs instead of image URLs.
- HTML pages, Google Images links, or hosts that block hotlinking.
- Temporary signed URLs that expire.
- Very large images; 600x900 is enough.

If no suitable cover exists, leave `CoverURL` out rather than using a broken link. The
app falls back to a placeholder, and a later pull request can add the real cover.

## Formatting rules

- Use UTF-8 and 4-space indentation, matching the existing files.
- Keep the two files as JSON arrays, even when a list has one entry.
- No trailing commas and no comments.
- Add new games to the end of `community_list.json`.
- Do not reorder or reformat unrelated entries. A focused diff is much easier to review.
- Omit optional keys that do not apply. Use `[]` when a list-valued field is required
  but empty.
- Use relative paths with escaped backslashes (`\\`) for Windows game paths.
- Do not include `CoverPath`, local file paths, API keys, tokens, or personal data.

## Before you open a pull request

Run these checks from the repository root:

```powershell
# Both files must parse as JSON
Get-Content lists/main_list.json -Raw | ConvertFrom-Json | Out-Null
Get-Content lists/community_list.json -Raw | ConvertFrom-Json | Out-Null

# IDs must be unique across both lists
$ids = @(
    Get-Content lists/main_list.json -Raw | ConvertFrom-Json
    Get-Content lists/community_list.json -Raw | ConvertFrom-Json
) | ForEach-Object ID

$duplicates = $ids | Group-Object | Where-Object Count -gt 1
if ($duplicates) { $duplicates | Format-Table Name, Count } else { "No duplicate IDs" }
```

Then confirm:

- [ ] The new entry is in `lists/community_list.json` and nowhere else.
- [ ] `ID` is lowercase, unique, and matches the game's Nexus domain when it has one.
- [ ] `Engine` is a recognized handler, or the game's engine name for a Hyura-only entry.
- [ ] Unreal Engine entries have correct `ModDirectories` paths checked against a real install.
- [ ] `CoverURL` opens as an image in a private browser window.
- [ ] Dependency `Link` values download an archive directly, without a login.
- [ ] The entry works in HMM: the game appears in Browse, the cover loads, a mod installs,
      and any dependency installs.
- [ ] No secrets, tokens, or local paths are included.

You can also run the full validator locally:

```powershell
python tools/validate_lists.py
```

The same script runs automatically as the **`validate-lists`** check on every pull
request. A pull request cannot be merged until that check passes.

## Review and approval

All changes to `main` go through a pull request. The `main` branch is protected:
direct pushes are disabled, at least one approval from the owner is required, stale
approvals are dismissed when new commits arrive, and force pushes and branch deletion
are blocked. The repository owner can bypass these rules for maintenance.

The owner checks:

- The entry matches the schema and the formatting rules.
- Paths, download links and cover URLs are correct.
- The game is actually moddable, and the engine handler or Hyura package matches how
  its mods are installed.
- Nothing unsafe, malicious, or unrelated is included.

Community entries may be promoted to `lists/main_list.json` once they have been tested
and are known to work well. Promotion does not change how the game works in HMM.

## Reporting a problem

Open an issue if a game entry:

- has a broken cover or download link,
- installs files into the wrong folder,
- points at the wrong Nexus domain,
- or should be removed.

Include the game `ID`, what you expected, and what happened. For a broken link,
include the URL and the response you saw (for example, a 404).

For problems with HMM itself, use the
[Hyura-Mod-Manager repository](https://github.com/TaylorHyura/Hyura-Mod-Manager).

## Attribution

Game names, cover images, and trademarks belong to their respective owners. The
catalog is data used by HMM to install and manage mods; it does not grant rights to
any game or mod. HMM is not affiliated with Nexus Mods, any game publisher, or any
dependency author.
