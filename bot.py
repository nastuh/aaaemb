import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Global variables
MUTED_ROLE_NAME = "Muted"

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

# Moderation Commands

@bot.tree.command(name="ban", description="Ban a member from the server")
@app_commands.describe(
    member="The member to ban",
    reason="Reason for the ban"
)
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.ban(reason=reason)
    embed = discord.Embed(
        title="🔨 Member Banned",
        color=discord.Color.red(),
        description=f"{member.mention} has been banned"
    )
    embed.add_field(name="Reason", value=reason)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="kick", description="Kick a member from the server")
@app_commands.describe(
    member="The member to kick",
    reason="Reason for the kick"
)
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.kick(reason=reason)
    embed = discord.Embed(
        title="👢 Member Kicked",
        color=discord.Color.orange(),
        description=f"{member.mention} has been kicked"
    )
    embed.add_field(name="Reason", value=reason)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="mute", description="Mute a member")
@app_commands.describe(
    member="The member to mute",
    duration="Duration of mute (e.g., 30m, 1h, 1d)",
    reason="Reason for the mute"
)
@app_commands.checks.has_permissions(manage_roles=True)
async def mute(interaction: discord.Interaction, 
              member: discord.Member, 
              duration: str = "30m", 
              reason: str = "No reason provided"):
    # Implement your mute logic here
    muted_role = discord.utils.get(interaction.guild.roles, name=MUTED_ROLE_NAME)
    if not muted_role:
        muted_role = await interaction.guild.create_role(name=MUTED_ROLE_NAME)
        # Configure channel permissions for muted role
    
    await member.add_roles(muted_role)
    embed = discord.Embed(
        title="🔇 Member Muted",
        color=discord.Color.dark_grey(),
        description=f"{member.mention} has been muted for {duration}"
    )
    embed.add_field(name="Reason", value=reason)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="purge", description="Delete multiple messages")
@app_commands.describe(
    amount="Number of messages to delete (max 100)"
)
@app_commands.checks.has_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction, amount: app_commands.Range[int, 1, 100] = 5):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"Deleted {amount} messages", ephemeral=True, delete_after=5)

@bot.tree.command(name="warn", description="Warn a member")
@app_commands.describe(
    member="The member to warn",
    reason="Reason for the warning"
)
@app_commands.checks.has_permissions(kick_members=True)
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    embed = discord.Embed(
        title="⚠️ Member Warned",
        color=discord.Color.gold(),
        description=f"{member.mention} has been warned"
    )
    embed.add_field(name="Reason", value=reason)
    await interaction.response.send_message(embed=embed)

# Utility Commands

@bot.tree.command(name="userinfo", description="Get information about a user")
@app_commands.describe(
    member="The member to get info about"
)
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(
        title=f"ℹ️ User Info: {member}",
        color=member.color
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d"))
    embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d"))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="Get information about the server")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(
        title=f"ℹ️ Server Info: {guild.name}",
        color=discord.Color.blue()
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Owner", value=guild.owner.mention)
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"))
    await interaction.response.send_message(embed=embed)

# Error Handling

@ban.error
@kick.error
@mute.error
@purge.error
@warn.error
async def mod_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
    elif isinstance(error, app_commands.BotMissingPermissions):
        await interaction.response.send_message("I don't have permission to do that!", ephemeral=True)
    else:
        await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)

bot.run('your_token')
