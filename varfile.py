# ==================== BOT CONFIGURATION ====================
import os

# List of admin IDs — comma-separated in env: "123456,789012"
admins = [int(x) for x in os.environ["ADMIN_IDS"].split(",")]

# Auto-abortion time for unused codes (in seconds)
auto_abort = int(os.environ.get("AUTO_ABORT", str(6*60*60)))

# Send registration reminder to group every 10 registrations
group_stats = os.environ.get("GROUP_STATS", "true").lower() == "true"

# Your group ID (starts with -)
group_id = int(os.environ["GROUP_ID"])

# Your channel ID (starts with -)
channel_id = int(os.environ["CHANNEL_ID"])

# Test mode
test_mode = os.environ.get("TEST_MODE", "false").lower() == "true"

# Test group ID (only used when test_mode = True)
test_group_id = int(os.environ.get("TEST_GROUP_ID", "-100"))

# Test channel ID (only used when test_mode = True)
test_channel_id = int(os.environ.get("TEST_CHANNEL_ID", "-100"))

# Your bot token from @BotFather on Telegram
bot_token = os.environ["BOT_TOKEN"]

# Database file name (don't change this)
database = "database.fs"

# Your bot's username (without the @ symbol)
bot_username = os.environ["BOT_USERNAME"]

# ==================== MILESTONE SETTINGS ====================
# Comma-separated list of milestone targets in env: "50,100,200,500,1000"
milestones = [int(x) for x in os.environ.get("MILESTONES", "50,100,200,500,1000").split(",")]

# Don't change these - they're used internally
next_milestone_index = 0
milestone_reached = False
