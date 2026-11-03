import backend
from backend.wheretfissm import find_where_tf_my_mod_is

import sys
import os

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

mod_path = find_where_tf_my_mod_is()
print("Using Mod Path:", mod_path)

file_system = backend.FileSystem(mod_path)
computer_ids = file_system.get_available_computers()

def should_ignore(path):
    ignored_suffixes = ("~", ".tmp", ".temp", ".swp", ".bak")
    return path.endswith(ignored_suffixes)

class FolderMonitor(FileSystemEventHandler):
    def __init__(self, target_path):
        self.target_path = Path(target_path)
        self.events = {}

    def update_file(self, path):
        sc_path = str(Path(path).relative_to(self.target_path)).replace("\\", "/")

        with open(path, "r") as f:
            data = f.read()

        worked = file_system.write_path(sc_path, data)

        if not worked:
            print("Write failed:", sc_path)
        else:
            print("Updated file:", sc_path)

    def rename_file(self, src, dst):
        sc_pathA = str(Path(src).relative_to(self.target_path)).replace("\\", "/")
        sc_pathB = str(Path(dst).relative_to(self.target_path)).replace("\\", "/")

        worked = file_system.rename(sc_pathA, sc_pathB)

        if not worked:
            print("Rename failed:", sc_pathA, sc_pathB)
        else:
            print("Renamed file:", sc_pathA, sc_pathB)

    def create_file(self, path):
        sc_path = str(Path(path).relative_to(self.target_path)).replace("\\", "/")

        worked = file_system.new_file(sc_path)

        if not worked:
            print("Create file failed:", sc_path)
        else:
            print("Created file:", sc_path)

    def create_dir(self, path):
        sc_path = str(Path(path).relative_to(self.target_path)).replace("\\", "/")

        worked = file_system.new_dir(sc_path)

        if not worked:
            print("Create dir failed:", sc_path)
        else:
            print("Created dir:", sc_path)

    def delete_path(self, path):
        sc_path = str(Path(path).relative_to(self.target_path)).replace("\\", "/")

        worked = file_system.delete_path(sc_path)

        if not worked:
            print("Delete failed:", sc_path)
        else:
            print("Deleted:", sc_path)

    def update(self):
        for path in self.events:
            for event_type, event_data in self.events[path]["queue"]:
                if event_type == "modified":
                    self.update_file(path)

                elif event_type == "move":
                    self.rename_file(path, event_data)

                elif event_type == "create":
                    if event_data:
                        self.create_dir(path)
                    else:
                        self.create_file(path)

                elif event_type == "delete":
                    self.delete_path(path)


                else:
                    print(f"[WARNING] NotImplemented: '{event_type}' on '{path}'")

                self.events[path]["queue"].remove((event_type, event_data))

    def __add_event(self, path: str | bytes, event_type: str, data=None):
        if should_ignore(path):
            return

        if isinstance(path, bytes):
            path = path.decode()

        if path not in self.events:
            self.events[path] = {
                "queue": []
            }

        if len(self.events[path]["queue"]) == 0:
            self.events[path]["queue"].append((event_type, data))
            return

        for other_type, other_data in self.events[path]["queue"]:
            if other_type == event_type:
                if event_type == "modified":
                    return  # No need to update it twice


    def on_created(self, event):
        self.__add_event(event.src_path, event_type="create", data=event.is_directory)

    def on_deleted(self, event):
        self.__add_event(event.src_path, event_type="delete")

    def on_modified(self, event):
        if event.is_directory:
            return

        self.__add_event(event.src_path, event_type="modified")

    def on_moved(self, event):
        self.__add_event(event.src_path, event_type="move", data=event.dest_path)


def get_inputs():
    print("Computers Found:", computer_ids)
    target_computer = input("Enter target computer id: ")
    #target_computer = str(int(computer_ids[0]))

    if int(target_computer) not in computer_ids:
        raise ValueError("Invalid Target Computer ID")

    active_path = input("Active Path: ")

    return target_computer, active_path


def full_reload(active_path, path="/"):
    print(f"\rReloading Directory... {path}       ", end="")
    active_path = active_path.removesuffix("/")
    file_objects = file_system.list_dir(path)

    os.makedirs(active_path + path, exist_ok=True)

    for file_object in file_objects:
        sub_path = path + file_object.name if path.endswith("/") else path + "/" + file_object.name
        local_path = active_path + sub_path if sub_path.startswith("/") else active_path + "/" + sub_path

        if file_object.is_directory:
            full_reload(active_path, sub_path)

        else:
            file_content = file_object.read()

            if file_content is not None:
                with open(local_path, "w") as f:
                    f.write(file_content)

    if path == "/":
        print("\rReload Complete!")

def main(target_computer_id: str, target_path: str):
    if int(target_computer_id) not in computer_ids:
        raise ValueError("Invalid Target Computer ID")

    file_system.select_computer(int(target_computer_id))

    full_reload(target_path)

    observer = Observer()
    handler = FolderMonitor(target_path)

    observer.schedule(handler, target_path, recursive=True)
    observer.start()

    print(f"Monitoring: {target_path}")

    try:
        while True:
            handler.update()
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        main(*get_inputs())
