export function getAllowedChatImageTypes(): string[] {
  return window.ALLOWED_CHAT_IMAGE_TYPES ?? [];
}

export async function resizeImageFile(
  file: File,
  maxDimension: number = 1000
): Promise<File> {
  const allowedTypes = new Set(getAllowedChatImageTypes());
  if (!allowedTypes.has(file.type)) {
    throw new Error("Unsupported image type");
  }

  const objectUrl = URL.createObjectURL(file);
  try {
    const img = await new Promise<HTMLImageElement>((resolve, reject) => {
      const image = new Image();
      image.onload = () => resolve(image);
      image.onerror = () => reject(new Error("Failed to decode image"));
      image.src = objectUrl;
    });

    const { naturalWidth, naturalHeight } = img;
    if (naturalWidth <= maxDimension && naturalHeight <= maxDimension) {
      return file;
    }

    const scale = Math.min(
      maxDimension / naturalWidth,
      maxDimension / naturalHeight
    );
    const targetWidth = Math.max(1, Math.round(naturalWidth * scale));
    const targetHeight = Math.max(1, Math.round(naturalHeight * scale));

    const canvas = document.createElement("canvas");
    canvas.width = targetWidth;
    canvas.height = targetHeight;
    const ctx = canvas.getContext("2d");
    if (!ctx) {
      throw new Error("Could not get 2D canvas context");
    }
    ctx.drawImage(img, 0, 0, targetWidth, targetHeight);

    const outputType =
      file.type === "image/jpeg" || file.type === "image/webp"
        ? file.type
        : "image/png";
    const quality =
      outputType === "image/jpeg" || outputType === "image/webp"
        ? 0.9
        : undefined;

    const blob = await new Promise<Blob>((resolve, reject) => {
      canvas.toBlob(
        (result) => {
          if (result) {
            resolve(result);
          } else {
            reject(new Error("Failed to encode resized image"));
          }
        },
        outputType,
        quality
      );
    });

    const baseName = file.name.replace(/\.[^.]+$/, "") || "pasted-image";
    const ext =
      outputType === "image/jpeg"
        ? "jpg"
        : outputType === "image/webp"
        ? "webp"
        : "png";
    return new File([blob], `${baseName}.${ext}`, { type: outputType });
  } finally {
    URL.revokeObjectURL(objectUrl);
  }
}
