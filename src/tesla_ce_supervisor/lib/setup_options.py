import typing
import zipfile
from io import BytesIO


class SetupOptionsCommand:
    """
        Deployment command
    """
    description: str
    command: str

    def to_json(self) -> dict:
        return {
            'description': self.description,
            'command': self.command
        }


class SetupOptionsFile:
    """
        Deployment file
    """
    description: str
    filename: str
    content: str
    mimetype: typing.Optional[str] = None

    def to_json(self) -> dict:
        return {
            'description': self.description,
            'filename': self.filename,
            'content': self.content,
            'mimetype': self.mimetype
        }


class SetupOptions:
    """
        Deployment options
    """
    require_files: bool = False
    commands: typing.List[SetupOptionsCommand] = []
    files: typing.List[SetupOptionsFile] = []

    def add_command(self, command: str, description: str):
        cmd = SetupOptionsCommand()
        cmd.command = command
        cmd.description = description
        self.commands.append(cmd)

    def add_file(self, filename: str, description: str, content: str, mimetype: typing.Optional[str] = None):
        file = SetupOptionsFile()
        file.filename = filename
        file.description = description
        file.content = content
        file.mimetype = mimetype
        self.files.append(file)
        self.require_files = True

    def get_zip(self):
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zip:
            cmd_list = ''
            for cmd in self.commands:
                cmd_list += '# {}\n'.format(cmd.description)
                cmd_list += '{}\n\n'.format(cmd.command)
            zip.writestr('commands.txt', cmd_list)
            for file in self.files:
                zip.writestr(file.filename, file.content)
        return buffer.getvalue()

    def to_json(self) -> dict:
        commands = [cmd.to_json() for cmd in self.commands]
        files = [file.to_json() for file in self.files]
        return {
            'require_files': self.require_files,
            'commands': commands,
            'files': files
        }
