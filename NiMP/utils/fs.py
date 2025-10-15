import pathlib

def delete(*path: pathlib.StrPath):
    mysql_sock_path = pathlib.Path.joinpath(pathlib.Path.cwd(), path);
    if pathlib.Path.exists(mysql_sock_path, follow_symlinks=False):
        try:
            pathlib.Path.unlink(mysql_sock_path)
        finally:
            True
    else:
        return 0;
    return 1;