import discord
from discord import app_commands
import os
import time
import ids

# Intents einstellen
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.voice_states = True



#Client definieren
class MyClient(discord.Client):

    def __init__(self):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    async def on_ready(self):
        print(f"Bot ist online als {self.user}")
        await self.tree.sync()
        print("Aktuelle Guilds:")
        for g in client.guilds:
            print(f"- {g.name} (ID: {g.id})")
            for voice_channel in g.voice_channels:
                if voice_channel.name == "Freier Channel" or voice_channel.name.endswith("'s Channel"):
                    text_channel = voice_channel.guild.get_channel(voice_channel.id)
                    async for message in text_channel.history(limit=2):
                        if message.author == client.user:
                            await message.delete()
                    await send_embed_panel(text_channel)
        activity = discord.Activity(type=discord.ActivityType.listening, name="/help")
        await client.change_presence(activity=activity)

client = MyClient()

# Help-Slash-Command
@client.tree.command(name="help", description="Gibt dir Infos über mich!")
#@app_commands.describe(kanal="Wähle einen Kanal",
                       #nachricht="Gib eine Nachricht ein")
async def help_command(interaction: discord.Interaction,
                        kanal: discord.TextChannel, nachricht: str):
    await kanal.send("""Hallo, hier findest du alle meine Funktionen!
                     [Sprachkanal erstellen] - Wenn du diesem Channel joinst, wird automatisch dein eigener Channel erstellt. In dem Chat von dem Voice Channel kannst du ihn dann anpassen!
                     Knopf 'Beanspruchen'    - Damit kannst du einen Channel der niemandem gehört beanspruchen. Immer wenn der Owner eines Channels den Channel verlässt, wird der Channel freigegeben.
                     Knopf 'Limit'           - Damit kannst du das Limit an Usern für deinen Channel einstellen. So kannst du z.B. nur 4 Personen deinem Channel joinen lassen. Zudem können unendlich viele joinen, wenn du als Limit 0 setzt. (Normal Einstellung)
                     Knopf 'Verstecken'      - Damit kannst du deinen Channel verstecken, dass nur die Leute in diesem Channel diesen sehen können. So kannst du verhindern, dass unberechtigte Leute deinem Channel joinen.
                     Knopf 'Zeigen'          - Damit kannst du deinen Channel wieder zeigen lassen, wenn du ihn versteckt hattest. So können wieder alle Personen deinem Channel joinen!""")


#Voice Channel erstellen
@client.event
async def on_voice_state_update(member, before, after):
    # Prüfen, ob der User einem Voice-Channel beigetreten ist

    #Löschen des VoiceChannels
    if before.channel is not None:
        if before.channel.name == "[Sprachkanal erstellen]":
            return
        member_count = len(before.channel.members)
        if member_count == 0:
            await before.channel.delete()
            return
        await checkName(before.channel, member)

    if after.channel is not None:
        if after.channel.name == "[Sprachkanal erstellen]":  #Erstellen des VoiceChannels
            print("afterchannel")
            category = after.channel.category
            guild = after.channel.guild
            new_channel = await guild.create_voice_channel(
                name=f"{member.display_name}'s Channel", category=category)
            await member.move_to(new_channel)
            text_channel = new_channel.guild.get_channel(new_channel.id)
            await send_embed_panel(text_channel)
            time.sleep(1)

async def checkName(channel, member):
    if channel.name == "Freier Channel":
        return
    owner_name = channel.name.replace("'s Channel", "")
    if owner_name == member.display_name:
        await channel.edit(name="Freier Channel")

async def send_embed_panel(text_channel):
    embed = discord.Embed(
        title="Konfigurator",
        description=
        "Herzlich Willkommen im Konfigurator dieses Voicechannels. Bitte drücke auf die Knöpfe, um jeweilige Befehle auszuführen!",
        color=discord.Color.blue())
    await text_channel.send(embed=embed)
    await buttonOwner(text_channel)

async def buttonOwner(text_channel):

    async def button_callback(interaction):  #Owner
        member = interaction.user
        voice_state = interaction.user.voice
        if voice_state is None:
            await interaction.response.send_message("Du musst diesem Voice Channel erst joinen, damit du diesen beanspruchen kannst!", ephemeral=True)
            return
        if text_channel.name == "Freier Channel" or interaction.user.display_name == "Bricker":
            await text_channel.edit(name=f"{member.display_name}'s Channel")
            await interaction.response.send_message("Der Channel gehört nun dir: Mach was du willst!", ephemeral=True)
        else:
            await interaction.response.send_message('Dieser Voicechannel gehört schon jemandem! Probiere es nochmal, wenn der Voice Channel "Freier Channel" heißt', ephemeral=True)
                
    button = discord.ui.Button(label="Beanspruchen", style=discord.ButtonStyle.success)
    button.callback = button_callback
    view = discord.ui.View()
    view.add_item(button)
    await buttonMax(view, text_channel)

async def buttonMax(view, text_channel):

    async def button_callback(interaction):  #Owner
        channel = interaction.user.voice.channel
        owner_name = channel.name.replace("'s Channel", "")
        if owner_name != interaction.user.display_name:
            await interaction.response.send_message('Dieser Voicechannel gehört dir nicht!', ephemeral=True)
            return
        await interaction.response.send_modal(NumberModal())

        

    buttonMax = discord.ui.Button(label="Limit",style=discord.ButtonStyle.secondary)
    buttonMax.callback = button_callback
    view.add_item(buttonMax)
    await buttonHide(view, text_channel)

async def buttoHide(view, text_channel):

    async def button_callback(interaction):  #Owner
        channel = interaction.user.voice.channel
        owner_name = channel.name.replace("'s Channel", "")
        if owner_name != interaction.user.display_name:
            await interaction.response.send_message('Dieser Voicechannel gehört dir nicht!', ephemeral=True)
            return
        role = interaction.guild.default_role #Rolle suchen
        await channel.set_permissions(role, read_messages=False) #Channel bearbeiten
        #Alten Button aus View entfernen
        for item in view.children:
            if isinstance(item, discord.ui.Button) and item.label == "Verstecken":
                view.remove_item(item)
                break
        #Button einstellen
        buttonMax = discord.ui.Button(label="Zeigen",style=discord.ButtonStyle.green)
        view.add_item(buttonMax)
        buttonMax.callback = button_callback
        #Vorherige Nachricht löschen
        async for message in text_channel.history(limit=1):
            if message.author == client.user:
                await message.delete()
        await sendButtons(text_channel, view) #Buttons anzeigen
        await interaction.response.send_message("Der Channel wurde Versteckt!", ephemeral=True) #Information

        

    buttonMax = discord.ui.Button(label="Verstecken",style=discord.ButtonStyle.red)
    buttonMax.callback = button_callback
    view.add_item(buttonMax)
    await sendButtons(text_channel, view)
   
async def buttonHide(view, text_channel):

    async def button_callback(interaction):  #Owner
        channel = interaction.user.voice.channel
        owner_name = channel.name.replace("'s Channel", "")
        if owner_name != interaction.user.display_name:
            await interaction.response.send_message('Dieser Voicechannel gehört dir nicht!', ephemeral=True)
            return
        for item in view.children:
            if item.label == "Verstecken":
                role = interaction.guild.default_role #Rolle suchen
                await channel.set_permissions(role, read_messages=False) #Channel bearbeiten
                #Alten Button aus View entfernen
                for item in view.children:
                    if isinstance(item, discord.ui.Button) and item.label == "Verstecken":
                        view.remove_item(item)
                        break
                #Button einstellen
                buttonHide = discord.ui.Button(label="Zeigen",style=discord.ButtonStyle.primary)
                view.add_item(buttonHide)
                buttonHide.callback = button_callback
                #Vorherige Nachricht löschen
                await interaction.message.edit(view=view)
                await interaction.response.send_message("Der Channel wurde Versteckt!", ephemeral=True) #Information
            if item.label == "Zeigen":
                role = interaction.guild.default_role #Rolle suchen
                await channel.set_permissions(role, read_messages=True) #Channel bearbeiten
                #Alten Button aus View entfernen
                for item in view.children:
                    if isinstance(item, discord.ui.Button) and item.label == "Zeigen":
                        view.remove_item(item)
                        break
                #Button einstellen
                buttonHide = discord.ui.Button(label="Verstecken",style=discord.ButtonStyle.red)
                view.add_item(buttonHide)
                buttonHide.callback = button_callback
                #Vorherige Nachricht löschen
                await interaction.message.edit(view=view)
                await interaction.response.send_message("Der Channel wurde wieder für alle geöffnet!", ephemeral=True) #Information
        

    buttonHide = discord.ui.Button(label="Verstecken",style=discord.ButtonStyle.red)
    buttonHide.callback = button_callback
    view.add_item(buttonHide)
    await sendButtons(text_channel, view)

async def sendButtons(text_channel, view):
    await text_channel.send('', view=view)
    #await text_channel.send('', view=viewMax)

#Maximalzahl Formular:
class NumberModal(discord.ui.Modal, title="Maximum einstellen"):
    number = discord.ui.TextInput(label="Bitte gib ein Maximum an", placeholder="z.B. 42", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        voice_state = interaction.user.voice
        if voice_state is None:
            await interaction.response.send_message("Du bist in keinem Voicechannel!", ephemeral=True)
            return

        channel = voice_state.channel  # Richtiger Zugriff auf VoiceChannel

        try:
            limit = int(self.number.value)
        except ValueError:
            await interaction.response.send_message("Bitte gib eine gültige Zahl ein!", ephemeral=True)
            return

        await channel.edit(user_limit=limit)
        await interaction.response.send_message(f"Das Limit wurde auf {limit} gesetzt!", ephemeral=True)




client.run(ids.DISCORD_TOKEN)
