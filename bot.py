import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Bot setup with better intents configuration
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    help_command=None,
    activity=discord.Activity(type=discord.ActivityType.watching, name="over the server")
)

# Constants
MUTED_ROLE_NAME = "🔇 Muted"
COLORS = {
    "red": 0xFF0000,
    "orange": 0xFFA500,
    "green": 0x00FF00,
    "blue": 0x0000FF,
    "purple": 0x800080
}

# Helper functions
async def create_muted_role(guild):
    """Create muted role with proper permissions"""
    muted_role = await guild.create_role(
        name=MUTED_ROLE_NAME,
        color=discord.Color.dark_grey(),
        reason="Muted role creation"
    )
    
    # Apply permissions to all channels
    for channel in guild.channels:
        await channel.set_permissions(
            muted_role,
            send_messages=False,
            add_reactions=False,
            speak=False,
            connect=False
        )
    return muted_role

def create_embed(title, description, color_name="blue"):
    """Create consistent embeds"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=COLORS.get(color_name, 0x0000FF),
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text=f"Bot {bot.user.name}")
    return embed

# Events
@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} is online!')
    print(f'🔗 Invite URL: {discord.utils.oauth_url(bot.user.id)}')
    
    try:
        synced = await bot.tree.sync()
        print(f'🔄 Synced {len(synced)} slash commands')
    except Exception as e:
        print(f'❌ Error syncing commands: {e}')

# Moderation Commands Group
moderation = app_commands.Group(name="mod", description="Moderation commands")

@moderation.command(name="ban", description="Ban a member from the server")
@app_commands.describe(
    member="Member to ban",
    reason="Reason for ban",
    delete_days="Number of days of messages to delete (0-7)"
)
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, 
              member: discord.Member, 
              reason: str = "No reason provided",
              delete_days: app_commands.Range[int, 0, 7] = 1):
    
    embed = create_embed(
        "🔨 Member Banned",
        f"{member.mention} has been banned",
        "red"
    )
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Messages Deleted", value=f"{delete_days} day(s)", inline=False)
    
    await member.ban(reason=reason, delete_message_days=delete_days)
    await interaction.response.send_message(embed=embed)

@moderation.command(name="tempban", description="Temporarily ban a member")
@app_commands.describe(
    member="Member to tempban",
    duration="Ban duration (e.g. 2d, 1w)",
    reason="Reason for tempban"
)
@app_commands.checks.has_permissions(ban_members=True)
async def tempban(interaction: discord.Interaction,
                 member: discord.Member,
                 duration: str,
                 reason: str = "No reason provided"):
    
    # Convert duration to seconds
    time_units = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    try:
        duration_num = int(duration[:-1])
        duration_unit = duration[-1].lower()
        total_seconds = time_units[duration_unit] * duration_num
    except:
        return await interaction.response.send_message("Invalid duration format! Use: 1h, 2d, 1w etc.", ephemeral=True)
    
    await member.ban(reason=f"Tempban: {reason}")
    embed = create_embed(
        "⏳ Member Temporarily Banned",
        f"{member.mention} has been banned for {duration}",
        "orange"
    )
    embed.add_field(name="Reason", value=reason, inline=False)
    await interaction.response.send_message(embed=embed)
    
    # Schedule unban
    await asyncio.sleep(total_seconds)
    await interaction.guild.unban(member)
    await interaction.followup.send(f"{member.mention} has been automatically unbanned after {duration}")

# New Fun Commands
@bot.tree.command(name="avatar", description="Get a user's avatar")
@app_commands.describe(member="Member to get avatar from")
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = create_embed(
        f"🖼️ {member.name}'s Avatar",
        "",
        "purple"
    )
    embed.set_image(url=member.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="poll", description="Create a simple poll")
@app_commands.describe(
    question="Poll question",
    option1="First option",
    option2="Second option"
)
async def poll(interaction: discord.Interaction,
              question: str,
              option1: str,
              option2: str):
    
    embed = create_embed(
        f"📊 Poll: {question}",
        f"1️⃣ {option1}\n\n2️⃣ {option2}",
        "green"
    )
    embed.set_author(name=f"Poll by {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
    
    message = await interaction.response.send_message(embed=embed)
    await message.add_reaction("1️⃣")
    await message.add_reaction("2️⃣")

# Help Command
@bot.tree.command(name="help", description="Show all available commands")
async def help(interaction: discord.Interaction):
    embed = create_embed(
        "ℹ️ Bot Help Menu",
        "Here are all available commands:",
        "blue"
    )
    
    embed.add_field(
        name="🛡️ Moderation",
        value="`/mod ban` - Ban a member\n"
              "`/mod tempban` - Temporarily ban\n"
              "`/mod kick` - Kick a member\n"
              "`/mod mute` - Mute a member\n"
              "`/mod purge` - Delete messages",
        inline=False
    )
    
    embed.add_field(
        name="🎉 Fun",
        value="`/poll` - Create a poll\n"
              "`/avatar` - Show user avatar\n"
              "`/userinfo` - Get user info",
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ Utility",
        value="`/serverinfo` - Server statistics\n"
              "`/help` - This menu",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Error Handling
@bot.event
async def on_app_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        embed = create_embed(
            "❌ Permission Denied",
            "You don't have permission to use this command!",
            "red"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    elif isinstance(error, app_commands.BotMissingPermissions):
        embed = create_embed(
            "❌ Bot Missing Permissions",
            "I don't have the required permissions to execute this command!",
            "red"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = create_embed(
            "❌ An Error Occurred",
            f"```{error}```",
            "red"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        raise error

# Add the command groups
bot.tree.add_command(moderation)

# Run the bot
if __name__ == "__main__":
    bot.run(TOKEN)
