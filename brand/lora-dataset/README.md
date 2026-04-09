# PatientPartner LoRA Training Dataset

Ready-to-upload dataset for FAL Flux 2 Trainer. Assembles brand imagery from patientpartner.com.

## Contents

- **patientpartner-lora-dataset.zip** — Upload this to [fal.ai/models/fal-ai/flux-2-trainer](https://fal.ai/models/fal-ai/flux-2-trainer)
- **patientpartner-photos/** — Source images + caption `.txt` files (same as zip contents)

## Regenerating the Dataset

```bash
cd ~/projects/patientpartner-master
python3 scripts/assemble-lora-dataset.py
```

Scrapes: homepage, about-us, how-patientpartner-works, pharma-engagement-software.

## Upload to FAL

1. Go to [fal.ai/models/fal-ai/flux-2-trainer](https://fal.ai/models/fal-ai/flux-2-trainer)
2. Upload `patientpartner-lora-dataset.zip`
3. Set **Default Caption** (if you didn't use per-image .txt files):
   ```
   PatientPartner brand style, warm natural lighting, teal and navy color palette #74CCD3 and #314D69, professional approachable mood, healthcare-adjacent without clinical coldness, diverse representation, clean modern composition.
   ```
4. Steps: 1000 | Learning rate: 0.00005
5. Click **Run**
6. When finished, use trigger phrase: `patientpartner style`

## Adding More Images

To include LinkedIn posts or brand guideline photos:

1. Add images to `patientpartner-photos/` as `patientpartner_36.png`, `patientpartner_37.jpg`, etc.
2. Add matching `patientpartner_36.txt`, `patientpartner_37.txt` with the same caption format
3. Re-run the script (it will overwrite the zip) or manually zip the folder
