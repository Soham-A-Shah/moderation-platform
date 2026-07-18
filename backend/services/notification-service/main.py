from moderation_common.events import consume_forever


def handle(event, producer):
    notification = {
        "user_id": event.get("user_id"),
        "content_id": event.get("content_id"),
        "message": f"Content decision: {event.get('final_decision')}",
    }

    print(f"[notification-service] {notification}", flush=True)


if __name__ == "__main__":
    consume_forever("notification-service", "moderation.completed", handle)
