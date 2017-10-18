import os
import shutil
import argparse

def populate_template(template,file_out,**kwargs):
    with open(template,'r') as ftmp:
        with open(file_out,'w') as fout:
            fout.write(ftmp.read().format(**kwargs))

def wrap_model(repo,model_folder,model_name,version,REST=True,out_folder=None,force_erase=False):
    if out_folder is None:
        out_folder = model_folder
    build_folder = out_folder+'/build'
    if os.path.isdir(build_folder):
        if not force_erase:
            print "Build folder already exists. To force erase, use --force argument"
            exit(0)
        else:
            shutil.rmtree(build_folder)
    shutil.copytree(model_folder,build_folder)
    shutil.copy2('./rest_microservice.py',build_folder)
    shutil.copy2("./grpc_microservice.py",build_folder)
    shutil.copy2('./seldon_model.py',build_folder)
    shutil.copy2("./seldon_requirements.txt",build_folder)
    shutil.copytree('./proto',build_folder+'/proto')
    populate_template(
        './Dockerfile.tmp',
        build_folder+'/Dockerfile',
        model_name=model_name,
        api_type="rest" if REST else "grpc"
    )
    populate_template(
        './Makefile.tmp',
        build_folder+'/Makefile',
        docker_repo=repo,
        docker_image_name=model_name.lower(),
        version=version)
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Utility script to wrap a python model into a docker build")
    
    parser.add_argument("model_folder",type=str)
    parser.add_argument("model_name",type=str)
    parser.add_argument("version",type=str)
    parser.add_argument("repo",type=str)
    parser.add_argument("--grpc",action="store_true")
    parser.add_argument("--out-folder",type=str,default=None)
    parser.add_argument("-f","--force",action="store_true")

    args = parser.parse_args()

    wrap_model(
        args.repo,
        args.model_folder,
        args.model_name,
        args.version,
        REST=not args.grpc,
        out_folder=args.out_folder,
        force_erase=args.force)
