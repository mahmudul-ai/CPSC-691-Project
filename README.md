# Brain Tumour Visualization Using NPR Techniques

An interactive 3D viewer that turns a brain MRI scan and its tumour segmentation into 3D models and displays them together: the brain as a see-through shell and the tumour as a solid red object outlined with white edges. You can rotate the model with the mouse and slice through it with the keyboard.

Final project for **CPSC 691: Rendering**, University of Calgary, Fall 2024.

---

## Table of Contents
- [Overview](#overview)
- [How It Works](#how-it-works)
- [Rendering Techniques](#rendering-techniques)
- [Repository Structure](#repository-structure)
- [Dataset](#dataset)
- [Installation](#installation)
- [Usage](#usage)
- [Controls](#controls)
- [Future Work](#future-work)
- [Team](#team)
- [Acknowledgements](#acknowledgements)
- [License](#license)

---

## Overview

Radiologists usually read brain MRI one 2D slice at a time, which makes it hard to picture a tumour's full shape and where it sits inside the brain. This project builds a simple pipeline that:

1. Loads a brain MRI case from the BraTS dataset (four MRI sequences plus an expert tumour label).
2. Converts each volume into a 3D surface mesh with the **Marching Cubes** algorithm.
3. Renders the brain and tumour together in real time with **OpenGL**. Non-photorealistic (illustrative) techniques keep the tumour clearly visible inside the brain.

## How It Works

```
 NIfTI volumes (.nii.gz)          3D meshes (.obj)               Interactive viewer
┌──────────────────────┐   ┌──────────────────────────┐   ┌──────────────────────────┐
│ t1n, t1c, t2w, t2f   │──▶│ Marching Cubes           │──▶│ PyOpenGL + Pygame        │
│ seg (tumour label)   │   │ (scikit-image, trimesh)  │   │ transparent brain,       │
└──────────────────────┘   └──────────────────────────┘   │ outlined tumour, slicing │
   3D_mesh_generator.ipynb        output/*.obj            └──────────────────────────┘
                                                                 rendering.py
```

**Step 1: Look at the data** (`3D_mesh_generator.ipynb`, first cell)
Loads the segmentation and the four MRI sequences with `nibabel` and shows the same axial slice of each side by side.

**Step 2: Generate meshes** (`3D_mesh_generator.ipynb`, second cell)
For each volume:
- empty slices are dropped and the rest are stacked into a 3D volume;
- the volume is converted to a binary mask (every non-zero voxel counts as "inside");
- `skimage.measure.marching_cubes` extracts the surface;
- the mesh is saved as `output/output-<sequence>.obj` with `trimesh`.

For the MRI sequences this gives the outer surface of the head/brain. For `seg` it gives the surface of the whole tumour (all tumour labels merged).

**Step 3: Render** (`rendering.py`)
Loads the brain mesh (`output-t2w.obj`) and the tumour mesh (`output-seg.obj`), computes smooth vertex normals and draws both every frame at 30 FPS.

## Rendering Techniques

| Technique | How it is done | Why |
|---|---|---|
| Translucent brain | Alpha blending (50% opacity) with depth writes turned off for the brain | The tumour stays visible through the brain surface |
| Opaque tumour with edge outlines | Solid red fill, then the same mesh drawn again as white wireframe with lighting off | Makes the tumour stand out and shows its surface structure, an illustrative (NPR) style |
| Phong-style lighting | One OpenGL light with ambient, diffuse and specular parts, plus smooth per-vertex normals | Gives the shapes depth and readable curvature |
| Interactive slicing | An OpenGL clip plane (`GL_CLIP_PLANE0`) moved along the x-axis | Cuts the brain away to look inside |
| Auto-rotation + mouse rotation | A slow automatic turn about the y-axis combined with mouse-drag rotation | Shows the model from all sides |
| Vertex Buffer Objects | Vertices, normals and indices uploaded as VBOs and drawn with `glDrawElements` | Draws meshes with ~200k triangles efficiently |

## Repository Structure

```
CPSC-691-Project/
├── 3D_mesh_generator.ipynb   # Data preview + Marching Cubes mesh generation
├── rendering.py              # Main interactive viewer (run this)
├── load_obj.py               # Minimal .obj reader (vertices + triangle faces)
├── render_obj.py             # Draws a mesh with VBOs; optional wireframe edges
├── support_functions.py      # Smooth per-vertex normal calculation
├── requirements.txt          # Python dependencies (pinned versions)
├── data/
│   └── BraTS-GLI-00005-100/  # One sample BraTS case
│       ├── ...-t1n.nii.gz    # T1-weighted (native)
│       ├── ...-t1c.nii.gz    # T1-weighted with contrast
│       ├── ...-t2w.nii.gz    # T2-weighted
│       ├── ...-t2f.nii.gz    # T2-FLAIR
│       └── ...-seg.nii.gz    # Expert tumour segmentation
├── output/                   # Pre-generated meshes (ready to view)
│   ├── output-seg.obj        # Tumour  (~14k vertices, ~27k triangles)
│   ├── output-t2w.obj        # Brain   (~97k vertices, ~193k triangles)
│   └── output-t1n/t1c/t2f.obj
└── LICENSE
```

## Dataset

The sample case comes from the **BraTS (Brain Tumor Segmentation) challenge** dataset of multi-parametric brain MRI with expert tumour labels.

- Volume size: 182 × 218 × 182 voxels, 1 mm isotropic spacing
- Sequences: T1 native (t1n), T1 contrast-enhanced (t1c), T2 (t2w), T2-FLAIR (t2f)
- Segmentation labels in this case: 0 = background, 2 = peritumoral edema, 4 = enhancing tumour

Only one case is included, for demonstration. To use other cases, download BraTS data from the official challenge site, follow its data-use terms and cite the BraTS papers.

## Installation

Requires **Python 3.10+** and a machine with a display and OpenGL support.

```bash
git clone https://github.com/mahmudul-ai/CPSC-691-Project.git
cd CPSC-691-Project

python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
pip install jupyter      # only needed to re-run the notebook
```

## Usage

**Option A: view the pre-made meshes (fastest)**
```bash
python rendering.py
```
A 600 × 600 window opens showing the brain and the tumour.

**Option B: regenerate the meshes first**
```bash
jupyter notebook 3D_mesh_generator.ipynb
```
Run both cells. New `.obj` files are written to `output/`; then run `python rendering.py`.

To view another case, change `data_id` in the notebook and the two file paths near the top of `rendering.py`.

## Controls

| Input | Action |
|---|---|
| Left-click + drag | Rotate the model |
| ↑ / ↓ arrow keys | Move the slicing plane forward / back |
| Close window | Quit |

The model also rotates slowly on its own.

## Future Work

- Separate meshes and colours for each tumour sub-region (edema, enhancing tumour, necrotic core)
- Shader-based NPR styles (toon shading, silhouette edges, hatching)
- Automatic tumour segmentation with a deep learning model instead of relying on the expert label
- A browser-based viewer so no local Python/OpenGL setup is needed

## Team

- Mahmudul Haque
- Mohammad Sakib Hossain

## Acknowledgements

- Course: CPSC 691 Rendering, University of Calgary
- Data: BraTS Challenge (Brain Tumor Segmentation)
- Libraries: nibabel, NumPy, scikit-image, trimesh, PyOpenGL, Pygame, Matplotlib

## License

Released under the [MIT License](LICENSE). The BraTS data keeps its original license and terms of use.
