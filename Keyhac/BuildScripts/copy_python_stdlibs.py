import os
import fnmatch
import shutil

#for name in os.environ:
#    print(f"env[{name}] = {os.environ[name]}")

framework_path = os.path.join( os.environ["TARGET_BUILD_DIR"], "Keyhac.app/Contents/Frameworks" )
resources_path = os.path.join( os.environ["TARGET_BUILD_DIR"], "Keyhac.app/Contents/Resources" )
print("Framework path:", framework_path)
print("Resources path:", resources_path)

python_version = "3.12"
src_dir = f"/Library/Frameworks/Python.framework/Versions/{python_version}/lib"
dst_dir = os.path.join( resources_path, "PythonLibs" )

def copytree( path, ignore_patterns=None ):

    src_dir2 = os.path.join(src_dir, path)
    dst_dir2 = os.path.join(dst_dir, path)

    for src_place, dirs, files in os.walk(src_dir2):
        
        def is_ignore(name):
            if ignore_patterns:
                for pattern in ignore_patterns:
                    if fnmatch.fnmatch(name, pattern):
                        return False
            return True
        
        dirs[:] = filter(is_ignore, dirs)
        files[:] = filter(is_ignore, files)

        assert src_place.startswith(src_dir2)
        place = src_place[len(src_dir2):].lstrip("/")
        dst_place = os.path.join(dst_dir2, place)
        
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

            

    #os.makedirs( os.path.join(dst_dir, path), exist_ok=True )
    #shutil.copytree( src_dir2, dst_dir2, ignore, dirs_exist_ok=True)


copytree( f"python{python_version}",
    ignore_patterns=(
        "__pycache__",
        "site-packages",
        "test",
    )
)
