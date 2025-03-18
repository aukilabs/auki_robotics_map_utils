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
- **`navmesh_endpoint`**: `https://dsc.auki.network/spatial/restricttonavmesh`
- **`routing_endpoint`**: `https://dsc.auki.network/spatial/pathfind`

> **Tip:** For security, you can add your robot as a **User** by assigning it to your organization.  

---

## Running the Map Extraction Script  

Use the following arguments when running the script:  

| **Argument**           | **Description**                                                                       |  
|-------------------------|---------------------------------------------------------------------------------------|  
| `--config CONFIG`       | Path to the YAML config file (if moved).                                              |  
| `--image-format {png,bmp,pgm}` | Image format for saving the map. Options: `png` (default), `bmp`, `stcm` or `pgm`.           |  
| `--resolution RESOLUTION` | Pixels per meter (default: 20, max: 200). Higher values result in more detailed maps. |  

`stcm` will return the proprietary map format used by Slamtec, a robotics and LiDAR specialist whose products are used in many service and utility robots.

### Example Command  

```bash  
python3 retrieve_map.py --image-format pgm --resolution 100  

# Note: This will generate a .pgm image at 0.01m per pixel resolution typically used by ROS / ROS2.
```


## Raycasting

A raycast is an invisible beam sent out from an origin point. It is then possible in the Domain to detect which digital objects this beam would hit. This is extremely important for linking the digital world with the physical world.

The pose of the origin is passed as an argument to the function **`get_raycast(pose)`** where pose is a transformation matrix. The transformation matrix is a combination of the rotation matrix (which defines the orientation) and the translation vector (which defines the position), applied to an object (such as a camera) in 3D space. The response will be a json string with the intersection point (as shown below):

**`{'message': 'Success', 'data': {'hits': [{'point': {'x': -2.3227962546392202, 'y': 0.675, 'z': 0.7821263074874878}, 'distance': 0.5104325206097033, 'normal': {'x': 0, 'y': 0, 'z': -1}, 'faceIndex': 4, 'name': '1451a9ca-2495-4932-bb5d-c97a4a8de6ce:0'}]}}`**

A simple example is provided.

The transformation matrix can be constructed as follows:

### Quaternion to Rotation Matrix

A quaternion `(r_x, r_y, r_z, w)` can be converted into a 3x3 rotation matrix as follows:

|                       |                       |                       |
|-----------------------|-----------------------|-----------------------|
| \( 1 - 2(r_y^2 + r_z^2) \) | \( 2(r_xr_y - wr_z) \) | \( 2(r_xr_z + wr_y) \) |
| \( 2(r_xr_y + wr_z) \) | \( 1 - 2(r_x^2 + r_z^2) \) | \( 2(r_yr_z - wr_x) \) |
| \( 2(r_xr_z - wr_y) \) | \( 2(r_yr_z + wr_x) \) | \( 1 - 2(r_x^2 + r_y^2) \) |

Where:

- `r_x`, `r_y`, `r_z` are the components of the quaternion (representing the axis of rotation).
- `w` is the scalar part of the quaternion (representing the cosine of half the rotation angle).

### Transformation Matrix

The 4x4 transformation matrix combines both rotation matrix (from above) and translation to transform an object in 3D space. It can be represented as:

|       |       |       |       |
|-------|-------|-------|-------|
| \( R_{11} \) | \( R_{12} \) | \( R_{13} \) | \( p_x \) |
| \( R_{21} \) | \( R_{22} \) | \( R_{23} \) | \( p_y \) |
| \( R_{31} \) | \( R_{32} \) | \( R_{33} \) | \( p_z \) |
| \( 0 \)       | \( 0 \)       | \( 0 \)       | \( 1 \)   |

Where:

- \( R_{ij} \) are the elements of the 3x3 rotation matrix, which defines the orientation of the object.
- \( p_x, p_y, p_z \) are the components of the translation vector, which defines the position of the object in 3D space.
- The last row \( [0, 0, 0, 1] \) ensures homogeneous coordinates for matrix multiplication.


## New functions - Navmesh Optimization

The Navmesh is the navigable pathway drawn in a Domain to set the walkable areas within the map. 

To maximise the use of the Navmesh we have added 2 endpoints and test functions.

Navmesh
---

The first is navmesh.py, designed to return the nearest point on the navmesh for a destination off-mesh, with the yaw set to face the goal. This was introduced for our Cactus based robots attempting to navigate to a product on a shelf, a solid object it clearly could not arrive at.

For example **`domain_server.get_navmesh_coord(target)`** would return **`{'x': 0, 'z':0, 'yaw': 0}`** where y is assumed to be 0 and at floor level.

Route Optimization
---
The second is route optimization, capable of plotting an array of waypoints which have been sorted accordingly, taking into account solid objects and navigable routes.

To optimize this further, we currently return 2 sets of data, original waypoints and onmesh waypoints to allow the user to choose which suits their use-case the best.

**`original_waypoints, onmesh_waypoints = domain_server.optimize_route(waypoints)`**, where waypoints are formatted **`{'x': 0, 'y': 0, 'z': 0}`**.