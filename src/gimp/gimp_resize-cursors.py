import os

from gimpfu import *


def resize_cursor_images(
    input_directory, output_directory, Copyright="", License="", other=""
):
    sizes = [24, 32, 36, 40, 48, 64]  # 24x24, 32x32, 36x36, 40x40, 48x48, 64x64

    # Ensure output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # List all files in the input directory
    for file_name in os.listdir(input_directory):
        # Only consider files without an extension for XMC files
        if "." in file_name:
            continue

        hot_spot_mapping = {
            "all-scroll": (6, 6),
            "bottom_left_corner": (4, 0),
            "bottom_right_corner": (4, 0),
            "bottom_side": (4, 0),
            "circle": (3, 3),
            "closedhand": (6, 6),
            "col-resize": (16, 26),
            "cross": (4, 4),
            "crossed_circle": (3, 3),
            "crosshair": (4, 4),
            "default": (0, 0),
            "dnd-move": (6, 6),
            "dnd-none": (6, 6),
            "dnd_no_drop": (3, 3),
            "down-arrow": (4, 0),
            "draft": (2, 0),
            "e-resize": (16, 26),
            "ew-resize": (16, 26),
            "fleur": (6, 6),
            "forbidden": (3, 3),
            "grab": (0, 0),
            "grabbing": (6, 6),
            "h_double_arrow": (16, 16),
            "half-busy": (0, 0),
            "hand1": (0, 0),
            "hand2": (0, 0),
            "help": (0, 0),
            "ibeam": (16, 23),
            "left-arrow": (4, 0),
            "left_ptr": (0, 0),
            "left_ptr_help": (0, 0),
            "left_ptr_watch": (0, 0),
            "left_side": (4, 0),
            "move": (6, 6),
            "n-resize": (4, 16),
            "ne-resize": (20, 20),
            "nesw-resize": (20, 20),
            "no_drop": (3, 3),
            "not_allowed": (3, 3),
            "ns-resize": (4, 16),
            "nw-resize": (11, 20),
            "nwse-resize": (11, 20),
            "openhand": (0, 0),
            "pencil": (2, 0),
            "pirate": (0, 0),
            "pointer": (0, 0),
            "pointing_hand": (0, 0),
            "progress": (0, 0),
            "question_arrow": (0, 0),
            "right-arrow": (4, 0),
            "right_side": (4, 0),
            "row-resize": (4, 16),
            "s-resize": (4, 16),
            "sb_h_double_arrow": (16, 26),
            "sb_v_double_arrow": (4, 16),
            "se-resize": (11, 20),
            "size-bdiag": (0, 0),
            "size-fdiag": (0, 0),
            "size-hor": (0, 0),
            "size-ver": (0, 0),
            "size_all": (6, 6),
            "size_bdiag": (20, 20),
            "size_fdiag": (11, 20),
            "size_hor": (16, 26),
            "size_ver": (4, 16),
            "split_h": (16, 26),
            "split_v": (4, 16),
            "sw-resize": (20, 20),
            "text": (16, 23),
            "top_left_arrow": (0, 0),
            "top_left_corner": (4, 0),
            "top_right_corner": (4, 0),
            "top_side": (4, 0),
            "up_arrow": (4, 0),
            "v_double_arrow": (4, 16),
            "w-resize": (16, 26),
            "wait": (0, 0),
            "watch": (0, 0),
            "whats_this": (0, 0),
            "xterm": (16, 23),
        }

        hot_spot_default = hot_spot_mapping.get(file_name, (0, 0))  # default is 32x32

        input_path = os.path.join(input_directory, file_name)
        output_path = os.path.join(output_directory, file_name)

        # Debug output
        print("Processing file:", input_path)

        for size in sizes:
            x_hot, y_hot = int(hot_spot_default[0] / 32 * size), int(
                hot_spot_default[1] / 32 * size
            )
            delay = 0
            try:
                # Load the XMC file
                print("Loading file...")
                image = pdb.file_xmc_load(input_path, input_path)
                drawable = pdb.gimp_image_get_active_layer(image)

                print("Setting interpolation:")
                pdb.gimp_context_set_interpolation(1)  # set interpolation to linear

                print("Scaling images...")
                pdb.gimp_image_scale(
                    image, size, size
                )  # (pdb.file_xmc_load(input_path, input_path), x={24, 32, 36, 40, 48, 64}, y={24, 32, 36, 40, 48, 64})

                # Save the resized XMC file
                print("Saving resized file...")
                pdb.file_xmc_save(
                    image,
                    drawable,
                    output_path,
                    output_path,
                    x_hot,  # x_hot
                    y_hot,  # y_hot
                    False,  # crop
                    size,  # size
                    True,  # size_replace
                    delay,  # delay
                    True,  # delay_replace
                    Copyright,  # copyright
                    License,  # license
                    other,  # other
                )
                # Close the image
                pdb.gimp_image_delete(image)
                print("Done processing.")

            except Exception as e:
                print("Failed processing:", input_path, str(e))
                gimp.message("Failed processing " + input_path + " " + str(e))


register(
    "python_fu_resize_cursor_images",
    "Batch resize Xcursor images",
    "Resize all Xcursor images in a directory",
    "Tenjin",
    "ashuramaruzxc/anime-cursors",
    "2024",
    "Resize Xcursors",
    "",  # Image types, leave blank for no specific types
    [
        (
            PF_DIRNAME,
            "input_directory",
            "Input Directory",
            "/Users/marie/Documents/development/anime-cursors/src/linux/Aya/cursors",
        ),
        (
            PF_DIRNAME,
            "output_directory",
            "Output Directory",
            "/Users/marie/Documents/development/anime-cursors/output",
        ),
        (PF_STRING, "copyright", "Input copyright information", ""),
        (PF_STRING, "license", "Input License information", ""),
        (PF_STRING, "other", "Input other information", ""),
    ],
    [],
    resize_cursor_images,
    menu="<Toolbox>/Xcursor",
)

main()
