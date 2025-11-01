from fastapi import APIRouter

misc_router = APIRouter(prefix="/api", tags=["misc"])

@misc_router.get("/features")
async def get_features():
    return [
        {
            "icon": "Zap",
            "title": "Parametric Templates",
            "description": "Create reusable, customizable 3D models with parameters that update in real-time.",
            "benefits": ["Real-time parameter updates", "Reusable design patterns", "Instant model regeneration"],
            "category": "Design"
        },
        {
            "icon": "Code",
            "title": "Multi-engine Support",
            "description": "Work with CadQuery, OpenSCAD, FreeCAD, and JSCAD in one unified interface. Switch between engines seamlessly.",
            "benefits": ["4 scripting languages", "Unified workflow", "Engine-specific optimizations"],
            "category": "Development"
        },
        {
            "icon": "Eye",
            "title": "Live 3D Preview",
            "description": "See your 3D models render instantly with our advanced three.js viewer. Rotate, zoom, and inspect every detail.",
            "benefits": ["Instant visual feedback", "High-quality rendering", "Interactive navigation"],
            "category": "Visualization"
        },
        {
            "icon": "GitBranch",
            "title": "Version Control",
            "description": "Track changes and iterations with built-in model versioning. Never lose your design progress again.",
            "benefits": ["Automatic versioning", "Change tracking", "Easy rollbacks"],
            "category": "Management"
        },
        {
            "icon": "Download",
            "title": "Multiple Export Formats",
            "description": "Export to STL, STEP, OBJ and other popular 3D formats. Ready for 3D printing, manufacturing, or further processing.",
            "benefits": ["STL for 3D printing", "STEP for CAD", "OBJ for graphics"],
            "category": "Export"
        },
        {
            "icon": "MessageSquare",
            "title": "Project Documentation",
            "description": "Document your design process with integrated chat history. Keep track of decisions and iterations.",
            "benefits": ["Design documentation", "Decision tracking", "Team collaboration"],
            "category": "Collaboration"
        }
    ]

@misc_router.get("/templates")
async def get_templates():
    return {
        "cadquery": """# CadQuery Example - Parametric Enclosure
import cadquery as cq

# Parameters
width = 80
height = 60
thickness = 20
wall_thickness = 3

# Create the main body
result = (cq.Workplane("XY")
    .box(width, height, thickness)
    .faces(">Z")
    .shell(-wall_thickness)
)

# Add mounting holes
result = (result
    .faces(">Z")
    .workplane()
    .pushPoints([(-width/2+10, -height/2+10), 
                 (width/2-10, -height/2+10),
                 (-width/2+10, height/2-10), 
                 (width/2-10, height/2-10)])
    .hole(3)
)""",
        "openscad": """// OpenSCAD Example - Parametric Enclosure
width = 80;
height = 60;
thickness = 20;
wall_thickness = 3;

difference() {
    cube([width, height, thickness]);
    translate([wall_thickness, wall_thickness, wall_thickness])
        cube([width-2*wall_thickness, height-2*wall_thickness, thickness]);
    
    // Mounting holes
    translate([10, 10, -1])
        cylinder(h=thickness+2, r=1.5);
    translate([width-10, 10, -1])
        cylinder(h=thickness+2, r=1.5);
    translate([10, height-10, -1])
        cylinder(h=thickness+2, r=1.5);
    translate([width-10, height-10, -1])
        cylinder(h=thickness+2, r=1.5);
}""",
        "freecad": """# FreeCAD Example - Parametric Enclosure
import FreeCAD as App
import Part

# Parameters
width = 80
height = 60
thickness = 20
wall_thickness = 3

# Create document
doc = App.newDocument()

# Create main box
box = Part.makeBox(width, height, thickness)

# Create inner box for hollowing
inner_box = Part.makeBox(
    width - 2*wall_thickness,
    height - 2*wall_thickness,
    thickness - wall_thickness
)
inner_box.translate(App.Vector(wall_thickness, wall_thickness, wall_thickness))

# Create hollow enclosure
enclosure = box.cut(inner_box)

# Add to document
Part.show(enclosure)""",
        "jscad": """// JSCAD Example - Parametric Enclosure
const { cube, cylinder } = require('@jscad/modeling').primitives
const { subtract, union } = require('@jscad/modeling').booleans
const { translate } = require('@jscad/modeling').transforms

const main = () => {
  const width = 80
  const height = 60
  const thickness = 20
  const wallThickness = 3
  
  // Main body
  const outer = cube({ size: [width, height, thickness] })
  const inner = cube({ 
    size: [width - 2*wallThickness, height - 2*wallThickness, thickness] 
  })
  
  const innerTranslated = translate(
    [wallThickness, wallThickness, wallThickness], 
    inner
  )
  
  // Create hollow enclosure
  const enclosure = subtract(outer, innerTranslated)
  
  // Add mounting holes
  const hole = cylinder({ radius: 1.5, height: thickness + 2 })
  const holes = [
    translate([10, 10, -1], hole),
    translate([width-10, 10, -1], hole),
    translate([10, height-10, -1], hole),
    translate([width-10, height-10, -1], hole)
  ]
  
  return subtract(enclosure, union(...holes))
}

module.exports = { main }"""
    }
