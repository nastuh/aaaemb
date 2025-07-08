# aaaemb

A feature-rich Discord moderation bot with slash commands, built with discord.py (v2.0+). Includes all essential moderation tools like ban, kick, mute, warn, and purge, plus utility commands.

![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## Features ✨

- **Modern Slash Commands** (/)
- **Full Moderation Suite**:
  - Ban/Kick members
  - Temporary mutes
  - Message purging
  - Warning system
- **User/Server Info**:
  - Detailed user profiles
  - Server statistics
- **Permission Management**
- **Error Handling**
- **Logging System**

## Commands List 📜

### Moderation 🔨
| Command | Description | Usage |
|---------|-------------|-------|
| `/ban` | Ban a member | `/ban member: @user reason: Spamming` |
| `/kick` | Kick a member | `/kick member: @user reason: Inappropriate name` |
| `/mute` | Mute a member | `/mute member: @user duration: 1h reason: Flooding chat` |
| `/warn` | Warn a member | `/warn member: @user reason: NSFW content` |
| `/purge` | Delete messages | `/purge amount: 50` |

### Utility ℹ️
| Command | Description | Usage |
|---------|-------------|-------|
| `/userinfo` | Get user details | `/userinfo member: @user` |
| `/serverinfo` | Get server stats | `/serverinfo` |

