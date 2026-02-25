Write-Host "=== FULL TRIGGER + AUTO-REPLY TEST ===" -ForegroundColor Cyan

# 1. Health Check
Write-Host "`n--- Health Check ---" -ForegroundColor Yellow
Invoke-RestMethod -Uri "http://localhost:8000/health"

# 2. Create a trigger (1 min delay)
Write-Host "`n--- Create Trigger (1 min delay) ---" -ForegroundColor Yellow
$trigger = @{
    name = "Demo Follow-up"
    trigger_type = "follow_up"
    channel = "whatsapp"
    recipient = "+919074285952"
    recipient_name = "Alice"
    message = "Hi Alice! I wanted to follow up on SalesPulse AI. Our tool can boost your reply rates by 3x. Would you be open to a quick 15-min demo this week?"
    delay_minutes = 1
    max_retries = 3
    stop_on_reply = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/triggers" `
  -Method POST -ContentType "application/json" -Body $trigger

# 3. Wait for trigger
Write-Host "`n--- Waiting 70s for trigger to fire... ---" -ForegroundColor Yellow
Start-Sleep -Seconds 20

# 4. Check trigger status
Write-Host "`n--- Trigger Status ---" -ForegroundColor Yellow
Invoke-RestMethod -Uri "http://localhost:8000/triggers"

# 5. Simulate lead reply
Write-Host "`n--- Simulate Lead Reply ---" -ForegroundColor Yellow
$reply = Invoke-RestMethod -Uri "http://localhost:8000/webhook/whatsapp" `
  -Method POST `
  -ContentType "application/x-www-form-urlencoded" `
  -Body "Body=Yes+I+am+interested+in+a+demo&From=whatsapp%3A%2B919074285952"
Write-Host $reply

# 6. Simulate follow-up
Write-Host "`n--- Simulate Follow-up ---" -ForegroundColor Yellow
$reply2 = Invoke-RestMethod -Uri "http://localhost:8000/webhook/whatsapp" `
  -Method POST `
  -ContentType "application/x-www-form-urlencoded" `
  -Body "Body=What+is+the+pricing?&From=whatsapp%3A%2B919074285952"
Write-Host $reply2

# 7. Conversation history
Write-Host "`n--- Conversation History ---" -ForegroundColor Yellow
Invoke-RestMethod -Uri "http://localhost:8000/conversations/%2B919074285952?limit=10"

Write-Host "`n=== TEST COMPLETE ===" -ForegroundColor Green