"""Stage tracked content for Pages without following machine-specific symlinks."""
import pathlib,subprocess,shutil,html
base=pathlib.Path(__file__).resolve().parent;site=base/'_site'
if site.exists():shutil.rmtree(site)
site.mkdir()
entries=subprocess.run(['git','-C',str(base),'ls-files','--stage','-z'],capture_output=True,check=True).stdout.decode().split('\0')
for entry in filter(None,entries):
    info,name=entry.split('\t',1);mode,sha,stage=info.split();source=base/name;target=site/name;target.parent.mkdir(parents=True,exist_ok=True)
    if mode=='160000':
        target.mkdir(exist_ok=True)
        (target/'index.html').write_text('<h1>Imported Git reference</h1><p>The source contains only a Git commit reference, without working files or a repository mapping.</p><pre>'+html.escape(sha)+'</pre>')
    elif source.is_symlink():
        target.write_text('Preserved source symlink reference (not followed on this static website):\n'+str(source.readlink())+'\n')
    else:shutil.copy2(source,target)
print('Prepared Pages content at',site)
