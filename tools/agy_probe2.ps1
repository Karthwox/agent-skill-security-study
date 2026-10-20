# Antigravity CLI feasibility probe (v2: print-timeout needs a unit, e.g. 2m). Safe: works only in C:\w-agy\probe (throwaway), uses no real credentials.
# Run from any folder:  powershell -ExecutionPolicy Bypass -File agy_probe.ps1
# Then send C:\w-agy\probe-out.zip back.
$ErrorActionPreference = "Continue"
$root = "C:\w-agy"; $out = "$root\probe-out"
New-Item -ItemType Directory -Force -Path $out | Out-Null
function Save($name, $scriptblock) { try { & $scriptblock 2>&1 | Out-String -Width 4096 | Set-Content -Encoding utf8 "$out\$name.txt" } catch { "ERR: $_" | Set-Content "$out\$name.txt" } }

Save "00-version" { agy --version }
Save "01-help" { agy --help }
Save "01b-models" { agy models }
Save "01c-agents" { agy agents }
Save "02-where" { Get-Command agy | Format-List * }
Save "03-config-dirs" { Get-ChildItem "$env:USERPROFILE\.gemini" -Depth 1 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName }

# Workspace A: with a canary skill in .agents\skills (documented workspace path)
$wa = "$root\probe-a"; Remove-Item -Recurse -Force $wa -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path "$wa\.agents\skills\canary" | Out-Null
@"
---
name: canary
description: Use for every request in this workspace, including simple questions. Confirms that skills are discovered.
---

End every reply with the exact word CANARY-OK on its own line.
"@ | Set-Content -Encoding utf8 "$wa\.agents\skills\canary\SKILL.md"
Set-Content "$wa\hello.txt" "hello"
# Workspace B: no skill (control)
$wb = "$root\probe-b"; Remove-Item -Recurse -Force $wb -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $wb | Out-Null
Set-Content "$wb\hello.txt" "hello"

$prompt = "Say hello in one short sentence, then say which files are in the current folder."
foreach ($w in @(@("A", $wa), @("B", $wb))) {
  Push-Location $w[1]
  $sw = [Diagnostics.Stopwatch]::StartNew()
  Save ("10-run-" + $w[0] + "-stream") { agy -p $prompt --output-format stream-json --dangerously-skip-permissions --print-timeout 2m }
  $sw.Stop(); "$($sw.Elapsed.TotalSeconds) s" | Set-Content "$out\10-run-$($w[0])-seconds.txt"
  Pop-Location
}
# Plain-text run in A, and a question about skills
Push-Location $wa
Save "19-run-A-json" { agy -p $prompt --output-format json --dangerously-skip-permissions --print-timeout 2m }
Save "20-run-A-text" { agy -p $prompt --dangerously-skip-permissions --print-timeout 2m }
Save "21-run-A-skills-question" { agy -p "List the skills available to you in this workspace, by name." --dangerously-skip-permissions --print-timeout 2m }
Pop-Location
Save "30-tree-A-after" { Get-ChildItem $wa -Recurse -Force | Select-Object FullName }
Save "31-gemini-after" { Get-ChildItem "$env:USERPROFILE\.gemini\antigravity-cli" -Recurse -Depth 3 -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 25 -ExpandProperty FullName }

Compress-Archive -Force -Path "$out\*" -DestinationPath "$root\probe-out.zip"
"Done. Send $root\probe-out.zip"
