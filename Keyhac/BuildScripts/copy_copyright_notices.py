import os
import fnmatch
import shutil

#for name in os.environ:
#    print(f"env[{name}] = {os.environ[name]}")

project_path = os.environ["PROJECT_DIR"]
resources_path = os.path.join( os.environ["TARGET_BUILD_DIR"], "Keyhac.app/Contents/Resources" )
print("Resources path:", resources_path)


def copy(src_filename, dst_filename):
    dst_dir = os.path.dirname(dst_filename)
    os.makedirs(dst_dir, exist_ok=True)

    src_stat = os.stat(src_filename)
    if os.path.exists(dst_filename):
        dst_stat = os.stat(dst_filename)
        if src_stat.st_mtime == dst_stat.st_mtime:
            return

    print(f"Copying {src_filename}")
    shutil.copy2(src_filename, dst_filename)


def copytree( src_dir, dst_dir, ignore_patterns=None ):

    for src_place, dirs, files in os.walk(src_dir):
        
        def is_ignore(name):
            if ignore_patterns:
                for pattern in ignore_patterns:
                    if fnmatch.fnmatch(name, pattern):
                        return False
            return True
        
        dirs[:] = filter(is_ignore, dirs)
        files[:] = filter(is_ignore, files)

        assert src_place.startswith(src_dir)
        place = src_place[len(src_dir):].lstrip("/")
        dst_place = os.path.join(dst_dir, place)
        
        os.makedirs(dst_place, exist_ok=True)
        
        for filename in files:
            src_filename = os.path.join(src_place, filename)
            dst_filename = os.path.join(dst_place, filename)
            
            src_stat = os.stat(src_filename)
            if os.path.exists(dst_filename):
                dst_stat = os.stat(dst_filename)
                if src_stat.st_mtime == dst_stat.st_mtime:
                    continue

            print(f"Copying {src_filename}")
            shutil.copy2(src_filename, dst_filename)


copy(
    os.path.join(project_path, "LICENSE"),
    os.path.join(resources_path, "CopyrightNotices", "Keyhac.txt")
)

copytree(
    os.path.join(project_path, "Keyhac/CopyrightNotices"),
    os.path.join(resources_path, "CopyrightNotices")
)

