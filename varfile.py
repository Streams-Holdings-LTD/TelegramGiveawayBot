import os

admins = [int(x) for x in os.environ.get("ADMIN_IDS", "8491280290").split(",")]

# Auto-abortion time for unused codes (in seconds)
auto_abort = int(os.environ.get("AUTO_ABORT", str(6*60*60)))

# Send registration reminder to group every 10 registrations
group_stats = os.environ.get("GROUP_STATS", "true").lower() == "true"

# Your group ID (starts with -)
group_id = int(os.environ.get("GROUP_ID", "-1003351933692"))

# Your channel ID (starts with -)
channel_id = int(os.environ.get("CHANNEL_ID", "-1003926125197"))

# Test mode
test_mode = os.environ.get("TEST_MODE", "false").lower() == "true"

# Test group ID (only used when test_mode = True)
test_group_id = int(os.environ.get("TEST_GROUP_ID", "-1003351933692"))

# Test channel ID (only used when test_mode = True)
test_channel_id = int(os.environ.get("TEST_CHANNEL_ID", "-1003926125197"))

# Your bot token from @BotFather on Telegram
bot_token = os.environ.get("BOT_TOKEN", "8791403335:AAFAuN-MLdjTOc2iLSIGsZaMlb0rLu8iIiE").strip().strip('"\'')
if not bot_token:
	raise ValueError("Missing BOT_TOKEN environment variable.")

# Database file name (don't change this)
database = "database.fs"

# Your bot's username (without the @ symbol)
bot_username = os.environ.get("BOT_USERNAME", "TopTokensGiveawayBot")

# ==================== MILESTONE SETTINGS ====================
# Comma-separated list of milestone targets in env: "50,100,200,500,1000"
milestones = [int(x) for x in os.environ.get("MILESTONES", "50,100,200,500,1000").split(",")]

# Don't change these - they're used internally
next_milestone_index = 0
milestone_reached = False