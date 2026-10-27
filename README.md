# GeoUnison

## Unifying Dense Visual Perception and Language Understanding for Multitask Earth Observation

GeoUnison is a remote-sensing vision–language model for natural-language-driven Earth observation. It brings together 17 task types across five capability families: captioning, classification, visual question answering, visual grounding and object detection, and segmentation.

## Release status

> **Core model code, pretrained model weights, and dataset release materials will be released soon.**

The manuscript is currently under review. This preview provides two lightweight utilities: an image-chat inference client and a bounding-box / mask visualizer. Core model implementation, model-serving code, weights, and datasets are not included yet.

## Available utilities

- `inference.py`: send ordered local images and a question to a user-provided image-capable chat-completions endpoint; print the answer and optionally save the response as JSON.
- `visualize.py`: overlay pixel-coordinate bounding boxes and binary masks, with a translucent fill and a visible contour.

Install the utility dependency with Python 3.10 or later:

```bash
pip install -r requirements.txt
```

### Inference client

The client requires an existing server implementing the image-chat API. No public GeoUnison endpoint or local model backend is bundled; this preview alone cannot run the GeoUnison model. The address below is an example for a server you operate, not a hosted demo. Images are sent only when you run the client, to the endpoint you specify.

```bash
python inference.py \
  --endpoint http://127.0.0.1:8000/v1/chat/completions \
  --model GeoUnison \
  --images path/to/image.png \
  --prompt "Describe the scene." \
  --output outputs/response.json
```

For multiple images, supply their paths after `--images` in the intended temporal order. If your server requires authentication, set `GEOUNISON_API_KEY` in your environment. The model name must match your server configuration. The client handles text responses; it does not derive masks or boxes from generated prose.

### Visualization

```bash
python visualize.py \
  --image path/to/image.png \
  --boxes path/to/boxes.json \
  --mask path/to/binary_mask.png \
  --output outputs/overlay.png
```

Supply `--boxes`, `--mask`, or both. A box file is a JSON list, for example `[{"xyxy": [10, 20, 80, 90], "label": "object"}]`. These are format examples, not model predictions. Coordinates are pixels in the original image. Masks must have the same dimensions as the image, with zero background and nonzero foreground. Neither script overwrites an existing output file intentionally. No example imagery or annotations are distributed in this preview.

## Planned releases

| Resource | Status |
| --- | --- |
| Inference client and visualization utilities | Available in this preview |
| Core model implementation and local inference backend | Will be released soon |
| Pretrained model weights and loading instructions | Will be released soon |
| Training code and configurations | Will be released soon |
| Evaluation code and benchmark protocols | Will be released soon |
| GeoUnison-10M dataset release materials and preparation tools | Will be released soon |
| GeoUnison-Bench dataset release materials and evaluation tools | Will be released soon |

We plan a staged release of the implementation, model weights, and data resources, accompanied by installation, inference, training, and evaluation documentation. Dataset distribution will follow the licenses of the original sources; download links and preparation instructions will be provided where redistribution is restricted.

Release announcements and download links will be added here as the resources become available.
