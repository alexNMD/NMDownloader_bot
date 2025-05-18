import requests


class DiscordAPI:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://discord.com/api/v10"
        self.headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type": "application/json"
        }

    def reply_with_embed(self, channel_id, message_id, title, description, color):
        """
        Répond à un message dans un canal Discord avec un embed.
        :param channel_id: ID du canal où le message a été envoyé.
        :param message_id: ID du message auquel répondre.
        :param title: Le titre de l'embed.
        :param description: La description de l'embed.
        :param color: La couleur de l'embed (en hexadécimal).
        :return: La réponse de l'API Discord.
        """
        url = f"{self.base_url}/channels/{channel_id}/messages/{message_id}/replies"

        embed = {
            "title": title,
            "description": description,
            "color": color,
        }

        data = {
            "embeds": [embed]
        }

        response = requests.post(url, headers=self.headers, json=data, timeout=10)
        return response.json()

    def send_embed(self, channel_id, title, description, color):
        """
        Envoie un message dans un canal Discord avec un embed (sans répondre à un autre message).
        :param channel_id: ID du canal où envoyer le message.
        :param title: Le titre de l'embed.
        :param description: La description de l'embed.
        :param color: La couleur de l'embed (en hexadécimal ou entier).
        :return: La réponse de l'API Discord.
        """
        url = f"{self.base_url}/channels/{channel_id}/messages"

        embed = {
            "title": title,
            "description": description,
            "color": color,
        }

        data = {
            "embeds": [embed]
        }

        response = requests.post(url, headers=self.headers, json=data, timeout=10)
        return response.json()

    def edit_embed(self, channel_id, message_id, title=None, description=None, color=None):
        """
        Modifie un embed dans un message existant dans un canal Discord.
        :param channel_id: ID du canal.
        :param message_id: ID du message à modifier.
        :param title: Nouveau titre de l'embed (optionnel).
        :param description: Nouvelle description de l'embed (optionnel).
        :param color: Nouvelle couleur de l'embed (en entier, optionnel).
        :return: La réponse de l'API Discord.
        """
        url = f"{self.base_url}/channels/{channel_id}/messages/{message_id}"

        embed = {}
        if title is not None:
            embed["title"] = title
        if description is not None:
            embed["description"] = description
        if color is not None:
            embed["color"] = color

        data = {
            "embeds": [embed]
        }

        response = requests.patch(url, headers=self.headers, json=data, timeout=10)
        return response.json()

    def send_message(self, channel_id, content):
        """
        Envoie un message à un canal Discord spécifié.
        :param channel_id: ID du canal Discord.
        :param content: Le contenu du message.
        :return: La réponse de l'API Discord.
        """
        url = f"{self.base_url}/channels/{channel_id}/messages"
        data = {
            "content": content
        }
        response = requests.post(url, headers=self.headers, json=data, timeout=10)
        response_json = response.json()
        return response_json.get('id')

    def edit_message(self, channel_id, message_id, new_content):
        """
        Modifie un message existant dans un canal Discord.
        :param channel_id: ID du canal où le message a été envoyé.
        :param message_id: ID du message à modifier.
        :param new_content: Nouveau contenu du message.
        :return: La réponse de l'API Discord.
        """
        url = f"{self.base_url}/channels/{channel_id}/messages/{message_id}"
        data = {
            "content": new_content
        }
        response = requests.patch(url, headers=self.headers, json=data, timeout=10)
        return response.json()

    def reply_to_message(self, channel_id, message_id, content):
        """
        Répond à un message dans un canal Discord.
        :param channel_id: ID du canal où le message a été envoyé.
        :param message_id: ID du message auquel répondre.
        :param content: Contenu de la réponse.
        :return: L'ID du message envoyé.
        """
        url = f"{self.base_url}/channels/{channel_id}/messages"
        data = {
            "content": content,
            "message_reference": {
                "message_id": message_id
            }
        }
        response = requests.post(url, headers=self.headers, json=data, timeout=10)
        response_json = response.json()
        return response_json.get('id')
