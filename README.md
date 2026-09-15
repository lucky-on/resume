# Sergey Didenko Web Resume

This folder is a self-contained static resume package for GitHub Pages. The public HTML intentionally omits the phone number; the published contact options are email and LinkedIn.

## Publish with GitHub Pages

1. Create or open the target GitHub repository.
2. Copy this folder's contents to the repository root, then commit and push them.
3. Open the repository's **Settings → Pages**. Under **Build and deployment**, select **Deploy from a branch**, choose the publishing branch, select the repository root (`/`), and save.
4. Wait for GitHub Pages to finish publishing, then open the generated site URL shown in the Pages settings.
5. Select **Download PDF** on the published site and confirm the resume opens or downloads correctly.

## Update the resume

After future content edits, rebuild the PDF from the repository root:

```sh
SERGEY_RESUME_PHONE="<phone-number>" python3 tools/build_resume_pdf.py
```

The builder requires `SERGEY_RESUME_PHONE` so the private contact detail is injected only during the PDF build. Keep the real value out of source files and do not commit local `.env` files.

Commit the rebuilt `assets/Sergey_Didenko_Resume.pdf` together with the related source changes, and repeat the published-site checks above.
