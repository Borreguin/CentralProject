from typing import List


class RemoteInfo:
    alias: str
    gitlink: str


class InfoTool:
    remotes: List[RemoteInfo]

    def toJson(self):
        return dict(remotes=self.remotes.__dict__)