import matplotlib.pyplot as plt
from PIL import Image as PILImage
import io


def display_langgraph(graph):
    """Visualize the graphs"""
    image_bytes = graph.get_graph().draw_mermaid_png()
    image = PILImage.open(io.BytesIO(image_bytes))

    # Use matplotlib to display the image
    plt.imshow(image)
    plt.axis("off")  # Hide axes
    plt.show()
