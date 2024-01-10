$venvName = "comments"

Write-Host "Activation de l'environnement virtuel $venvName..."
& ".\$venvName\Scripts\Activate"

Write-Host "Lancement du bot..."
& ".\$venvName\Scripts\python" ".\main.py"

Read-Host -Prompt "Press Enter to exit"