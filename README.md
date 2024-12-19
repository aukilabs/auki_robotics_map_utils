# AUKI Robotics  

Welcome to the **Auki Robotics** GitHub repository!  

This repository hosts tools and software for robotics systems, focusing on **precision mapping**, **navigation**, and **automation**. The posemesh is designed to enable seamless collaboration between devices, including robots, ensuring efficient and coordinated operation in dynamic environments.  

---

## Configuration  

All configuration information is accessible through your [Auki Network account](https://console.auki.network/login).  

You will need to add the following details in the `config/default.yaml` file:  

- **`domain_id`**: The ID of the domain you want the map for.  
- **`domain_server`**: Visible next to your domain in the **Domains** tab.  
- **`posemesh_account`**: Your console username (e.g., `user@website.com`).  
- **`posemesh_password`**: Your console password.  
- **`map_endpoint`**: `https://dsc.dev.aukiverse.com/spatial/crosssection`  
  *(No need to change this at this time.)*  

> **Tip:** For security, you can add your robot as a **User** by assigning it to your organization.  

---

## Running the Script  

Use the following arguments when running the script:  

| **Argument**           | **Description**                                                                       |  
|-------------------------|---------------------------------------------------------------------------------------|  
| `--config CONFIG`       | Path to the YAML config file (if moved).                                              |  
| `--image-format {png,bmp,pgm}` | Image format for saving the map. Options: `png` (default), `bmp`, or `pgm`.           |  
| `--resolution RESOLUTION` | Pixels per meter (default: 20, max: 200). Higher values result in more detailed maps. |  

### Example Command  

```bash  
python3 retrieve_map.py --image-format pgm --resolution 100  

# Note: This will generate a .pgm image at 0.01m per pixel resolution typically used by ROS / ROS2.
