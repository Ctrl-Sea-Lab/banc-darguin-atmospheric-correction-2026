"""Run bounded R models with the existing project environment and safe figure paths."""
from pathlib import Path
import os, subprocess, sys
A=Path(__file__).resolve().parents[1]; repo=A.parents[1]
sys.path.insert(0,str(repo/'scripts'))
from figure_io import generated_figure_path
for name in ['ctr56_temporal_gam.png','ctr56_temporal_gam.pdf','ctr56_uncertainty_coverage.png','ctr56_residual_diagnostics.png']:
 generated_figure_path(A,name).parent.mkdir(parents=True,exist_ok=True)
env_root=Path(os.environ.get('CTR56_ENV_ROOT','/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026'))
assert (env_root/'renv.lock').read_bytes()==(repo/'renv.lock').read_bytes()
assert (env_root/'uv.lock').read_bytes()==(repo/'uv.lock').read_bytes()
subprocess.run([str(env_root/'scripts/project-env.sh'),'Rscript',str(A/'scripts/ctr56_models.R'),str(A),str(A/'figures/generated')],check=True,env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'})
