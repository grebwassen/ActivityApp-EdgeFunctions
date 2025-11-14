import json
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.exception import AppwriteException
from appwrite.query import Query

def parse_event(req_body):
    """Parst das JSON, das Appwrite beim Aufruf sendet."""
    try:
        return json.loads(req_body)
    except:
        return {}

def main(req, res):
    event_data = parse_event(req.body)

    target_user_id = event_data.get("targetUserId")
    requester_id = event_data.get("requesterId")

    if not target_user_id:
        res.json({"error": "Missing targetUserId"}, status=400)
        return

    client = Client()
    client.set_endpoint("http://87.237.52.193:8080/v1")
    client.set_project("690b336e0021a28c8667")
    client.set_key("standard_ace33873d572ee352eadaba36c179403be7c9989011d72ef2c276e717becbdd223c44d84f57e6120bac3b837906575ce5b44839e2e663f69aed77750a158c009cb83f6ed1c97db26379784889dc60ff104652860c6c7e8ea49ced20321158d0b497fc09a4d4f8363a2ff5116e921fc523df7b092baf4188a870349801fdd9094")

    databases = Databases(client)

    try:
        response = databases.list_documents(
            database_id="690b69b50039d26ff931",
            collection_id="profile",
            queries=[Query.equal("userId", target_user_id)]
        )
        if len(response["documents"]) == 0:
            res.json({"error": "Profile not found"}, status=404)
            return
        
        profile = response["documents"][0]
        
    except AppwriteException as e:
        res.json({"error": str(e)}, status=404)
        return

    privacy = profile.get("privacyLevel", "public")

    visible_profile = {
        "userId": target_user_id,
        "username": profile.get("username"),
    }

    if privacy == "public":
        visible_profile["picture"] = profile.get("picture")

    elif privacy == "friends":
        if requester_id and requester_id in profile.get("friends", []):
            visible_profile["picture"] = profile.get("picture")

    elif privacy == "private":
        pass

    res.json(visible_profile, status=200)