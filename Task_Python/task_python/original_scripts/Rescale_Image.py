from PIL import Image

def rescale_image(image_path: str, new_size: tuple[int, int]):
    try:
        img = Image.open(image_path)
        img = img.resize(new_size)
        img.save("rescaled_image.jpg")
        print("Image rescaled successfully!")
    except Exception as e:
        print(f"Error: {e}")

def main():
    image_path = input("Enter the image path: ")
    width = int(input("Enter the new width: "))
    height = int(input("Enter the new height: "))
    new_size = (width, height)
    rescale_image(image_path, new_size)

if __name__ == "__main__":
    main()