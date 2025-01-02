# AUKI Robotics  

Welcome to the **Auki Robotics** GitHub repository!  

This repository hosts tools and software for robotics systems, focusing on **precision mapping**, **navigation**, and **automation**. The posemesh is designed to enable seamless collaboration between devices, including robots, ensuring efficient and coordinated operation in dynamic environments.  

---

## Configuration  

All configuration information is accessible through your [Auki Network account](https://console.auki.network/login).  

You will need to add the following details in the `config/default.yaml` file:  

- **`domain_id`**: The ID of the domain you want the map for.
- **`posemesh_account`**: Your console username (e.g., `user@website.com`).  
- **`posemesh_password`**: Your console password.  
- **`map_endpoint`**: `https://dsc.auki.network/spatial/crosssection`  
- **`raycast_endpoint`**: `https://dsc.auki.network/spatial/raycast`

> **Tip:** For security, you can add your robot as a **User** by assigning it to your organization.  

---

## Running the Map Extraction Script  

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
```


## New Function - Raycasting

A raycast is an invisible beam sent out from an origin point. It is then possible in the Domain to detect which digital objects this beam would hit. This is extremely important for linking the digital world with the real world.

The pose of the origin is passed as a transformation matrix, and the response will be a json string with the intersection point (as shown below):

**`{'message': 'Success', 'data': {'hits': [{'point': {'x': -2.3227962546392202, 'y': 0.675, 'z': 0.7821263074874878}, 'distance': 0.5104325206097033, 'normal': {'x': 0, 'y': 0, 'z': -1}, 'faceIndex': 4, 'name': '1451a9ca-2495-4932-bb5d-c97a4a8de6ce:0'}]}}`**

A simple example is provided.
