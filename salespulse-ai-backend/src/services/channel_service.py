from sqlalchemy.orm import Session
from models.channel import Channel
from schemas.channel import ChannelCreate, ChannelUpdate

class ChannelService:
    def __init__(self, db: Session):
        self.db = db

    def create_channel(self, channel_data: ChannelCreate) -> Channel:
        new_channel = Channel(**channel_data.dict())
        self.db.add(new_channel)
        self.db.commit()
        self.db.refresh(new_channel)
        return new_channel

    def get_channel(self, channel_id: int) -> Channel:
        return self.db.query(Channel).filter(Channel.id == channel_id).first()

    def update_channel(self, channel_id: int, channel_data: ChannelUpdate) -> Channel:
        channel = self.get_channel(channel_id)
        if channel:
            for key, value in channel_data.dict(exclude_unset=True).items():
                setattr(channel, key, value)
            self.db.commit()
            self.db.refresh(channel)
        return channel

    def delete_channel(self, channel_id: int) -> bool:
        channel = self.get_channel(channel_id)
        if channel:
            self.db.delete(channel)
            self.db.commit()
            return True
        return False

    def get_all_channels(self) -> list[Channel]:
        return self.db.query(Channel).all()