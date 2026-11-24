# Contributing to HMM Supported Games

Thanks for helping the HMM catalog grow. This repository holds only the game lists,
so most contributions are small JSON changes.

The full schema, examples, and validation checks live in the [README](README.md).
This page covers the workflow and what reviewers expect.

This catalog is the game-support part of the HMM project. Public releases and bug
reports live in [Hyura-Mod-Manager](https://github.com/TaylorHyura/Hyura-Mod-Manager),
and the application source is private during pre-release.

## Ways to contribute

- **Add a game.** Append one entry to `lists/community_list.json`.
- **Fix an entry.** Correct a path, download link, cover, name, or Nexus domain.
- **Remove a game.** Explain why it no longer works or should not be listed.
- **Report a problem.** Open an issue with the game `ID` and what went wrong.

Adding a game to the community list is preferred over opening a request and waiting.
You can test the entry locally in HMM before submitting it.

## Workflow

1. Fork the repository.
2. Create a branch with a short name, for example `add-game-my-game` or
   `fix-re4-cover`.
3. Make the smallest change that solves the problem.
4. Run the validator from the repository root (Python 3.10 or newer):

   ```powershell
   python tools/validate_lists.py
   ```

   Or run the JSON and duplicate-ID checks manually from the
   [README](README.md#before-you-open-a-pull-request).
5. Test the entry in HMM when possible.
6. Open a pull request against `main` and fill in the template.
7. Respond to review comments. The owner merges the pull request when it is ready.

Do not merge your own pull request, push directly to `main`, or force-push a branch
that is under review. `main` is protected and accepts changes through pull requests
only.

## What goes where

| Change | File |
| --- | --- |
| A new community-supported game | `lists/community_list.json` |
| A correction to an existing community game | `lists/community_list.json` |
| A correction to an officially supported game | Open an issue or pull request; the owner decides whether to edit `main_list.json` |
| A new officially supported game | Discuss it with the owner first |

New games normally start in the community list. The owner can promote a tested entry
to the official list later.

## Pull request scope

- **New game:** one game per pull request.
- **Fixes:** keep unrelated games out of the diff.
- **Formatting:** do not reorder or reformat existing entries. Reviewers should be able
  to see exactly what changed.
- **Promotions:** moving an entry from the community list to the official list should
  be its own pull request.

## Entry checklist

Before submitting, confirm:

- [ ] The file is valid JSON and uses 4-space indentation.
- [ ] The new game is appended to `lists/community_list.json`.
- [ ] `ID` is lowercase, unique across both lists, and matches the game's Nexus domain
      when it has one.
- [ ] `Engine` is a recognized handler (`UnrealEngine`, `REEngine`, `MTFramework` or
      `RenderWare`), or the game's engine name for a Hyura-only entry.
- [ ] Unreal Engine entries have `ModDirectories` paths checked against a real install.
- [ ] `CoverURL` is a direct HTTPS image link that works in a private browser window.
- [ ] Dependency `Link` values download an archive directly, without a login.
- [ ] The entry appears in HMM Browse, the cover loads, a mod installs, and any
      dependency installs.
- [ ] No `CoverPath`, local paths, API keys, tokens, or personal data are included.

See the [README](README.md) for the field reference, path rules, and cover guidance.

## Testing in HMM

Use a current HMM build, add the game from Browse, and try the parts the entry claims
to support:

1. The game appears under **Community Supported** with the expected name and cover.
2. A typical mod for that game installs to the expected folder.
3. Deployment, enable/disable, and restore work for that mod.
4. Every dependency installs from its `Link` and lands in the right place.

If you cannot test a particular step, say so in the pull request. That is better than
claiming it works.

## Commit messages

Use a short imperative subject, then add detail in the body when it helps:

```text
Add Clair Obscur: Expedition 33

Adds the community entry with the pak directory used by the game.
```

Avoid vague subjects such as `update`, `fix`, or `changes`.

## Review and approval

The repository owner reviews every pull request. Expect comments about:

- accuracy of paths, links, and metadata,
- whether the engine handler or Hyura package fits the game,
- duplicate or conflicting IDs,
- unrelated formatting changes,
- safety of download links.

The owner may edit the branch or ask you to update it. A pull request is merged only
after the owner approves it, the `validate-lists` check passes, and all review
conversations are resolved. Once merged, the change is live for HMM users on their next
catalog refresh.

## Security and privacy

- Never include API keys, access tokens, passwords, or personal file paths.
- Do not submit links to pirated games, mods, or tools.
- Report malicious or unsafe links in an issue instead of downloading them.
- If you accidentally commit a secret, say so in the pull request so it can be removed
  and rotated; deleting it in a later commit is not enough.

## Questions

Open an issue with the `question` label, or comment on an existing pull request. For
HMM itself, use the [Hyura-Mod-Manager repository](https://github.com/TaylorHyura/Hyura-Mod-Manager).
