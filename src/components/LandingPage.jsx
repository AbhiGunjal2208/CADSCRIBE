import React, { useState, useEffect } from 'react';
import { miscAPI } from '@/api';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/contexts/AuthContext';
import { Copy, Play, Zap, Code, Eye, GitBranch, Download, MessageSquare } from 'lucide-react';
import { toast } from 'sonner';
import heroImage from '@/assets/hero-image.jpg';


const iconMap = { Zap, Code, Eye, GitBranch, Download, MessageSquare };

export const LandingPage = () => {
  const { loginDemo } = useAuth();
  const navigate = useNavigate();
  const [activeTemplate, setActiveTemplate] = useState('cadquery');
  const [features, setFeatures] = useState([
    { id: 1, title: 'AI-Powered Design', description: 'Generate CAD models from natural language', icon: 'Zap' },
    { id: 2, title: 'Real-time Preview', description: 'See your designs come to life instantly', icon: 'Eye' },
    { id: 3, title: 'Code Generation', description: 'Export to multiple CAD formats', icon: 'Code' }
  ]);
  const [templates, setTemplates] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadLandingData = async () => {
      try {
        // Set a shorter timeout for landing page data
        const timeoutPromise = new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Request timeout')), 10000)
        );

        const [featuresResult, templatesResult] = await Promise.allSettled([
          Promise.race([miscAPI.getFeatures(), timeoutPromise]),
          Promise.race([miscAPI.getTemplates(), timeoutPromise])
        ]);

        // Handle features data
        if (featuresResult.status === 'fulfilled' && Array.isArray(featuresResult.value)) {
          setFeatures(featuresResult.value);
        } else {
          console.warn('Failed to load features, using fallback data');
        }

        // Handle templates data
        if (templatesResult.status === 'fulfilled' && templatesResult.value && typeof templatesResult.value === 'object') {
          setTemplates(templatesResult.value);
        } else {
          console.warn('Failed to load templates, using fallback data');
          // Set fallback templates
          setTemplates({
            cadquery: `# CadQuery Example - Parametric Enclosure
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
)`,
            openscad: `// OpenSCAD Example - Parametric Enclosure
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
}`,
            freecad: `# FreeCAD Example - Parametric Enclosure
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
Part.show(enclosure)`,
            jscad: `// JSCAD Example - Parametric Enclosure
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

module.exports = { main }`
          });
        }
      } catch (err) {
        console.error('Error loading landing data:', err);
        setError('Unable to connect to server. Using offline mode.');
      } finally {
        setLoading(false);
      }
    };

    loadLandingData();
  }, []);

  const handleDemoLogin = async () => {
    try {
      await loginDemo();
      navigate('/workspace/project-1');
      toast.success('Welcome to CADSCRIBE Demo!');
    } catch (error) {
      toast.error('Demo login failed');
    }
  };

  const copyTemplate = (template) => {
    navigator.clipboard.writeText(template);
    toast.success('Template copied to clipboard!');
  };

  if (loading) return <div className="text-center py-8">Loading...</div>;
  if (error) return <div className="text-center text-red-500 py-8">{error}</div>;

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="section-padding bg-gradient-to-br from-background via-background to-muted">
        <div className="container-main">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="animate-fade-in">
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground mb-6">
                Parametric CAD{' '}
                <span className="bg-gradient-hero bg-clip-text text-transparent">
                  Scripting
                </span>{' '}
                Made Simple
              </h1>
              <p className="text-xl text-muted-foreground mb-8 max-w-lg">
                Create, iterate, and export 3D models using Python, JavaScript, and other 
                programming languages. No complex GUI needed.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Button className="btn-hero" asChild>
                  <Link to="/auth/signup">Get Started Free</Link>
                </Button>
                <Button 
                  variant="outline" 
                  className="btn-outline-hero"
                  onClick={handleDemoLogin}
                >
                  <Play className="mr-2 h-4 w-4" />
                  Try Demo
                </Button>
              </div>
            </div>
            
            <div className="animate-slide-up">
              <div className="relative">
                <img 
                  src={heroImage} 
                  alt="CADSCRIBE 3D Modeling Interface" 
                  className="rounded-2xl shadow-large w-full h-auto"
                />
                <div className="absolute inset-0 bg-gradient-glass rounded-2xl"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="section-padding bg-muted/30">
        <div className="container-main">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-foreground mb-4">
              Everything You Need for CAD Scripting
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              CADSCRIBE brings together the best tools and workflows for parametric design
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => {
              const Icon = iconMap[feature.icon] || Zap;
              return (
                <Card key={index} className="card-feature">
                  <CardHeader>
                    <div className="w-12 h-12 bg-gradient-primary rounded-lg flex items-center justify-center mb-4">
                      <Icon className="h-6 w-6 text-primary-foreground" />
                    </div>
                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-base">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Templates Section */}
      <section className="section-padding">
        <div className="container-main">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-foreground mb-4">
              Start with Templates
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Choose your preferred scripting language and start building immediately
            </p>
          </div>

          <Tabs value={activeTemplate} onValueChange={setActiveTemplate} className="w-full">
            <TabsList className="grid w-full grid-cols-4 mb-8">
              <TabsTrigger value="cadquery" className="flex items-center gap-2">
                <Badge variant="secondary">Python</Badge>
                CadQuery
              </TabsTrigger>
              <TabsTrigger value="openscad" className="flex items-center gap-2">
                <Badge variant="secondary">OpenSCAD</Badge>
                OpenSCAD
              </TabsTrigger>
              <TabsTrigger value="freecad" className="flex items-center gap-2">
                <Badge variant="secondary">Python</Badge>
                FreeCAD
              </TabsTrigger>
              <TabsTrigger value="jscad" className="flex items-center gap-2">
                <Badge variant="secondary">JS</Badge>
                JSCAD
              </TabsTrigger>
            </TabsList>

            {Object.entries(templates).map(([key, template]) => (
              <TabsContent key={key} value={key}>
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between">
                    <div>
                      <CardTitle className="capitalize">{key} Template</CardTitle>
                      <CardDescription>
                        Get started with this parametric enclosure example
                      </CardDescription>
                    </div>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => copyTemplate(template)}
                      className="flex items-center gap-2"
                    >
                      <Copy className="h-4 w-4" />
                      Copy
                    </Button>
                  </CardHeader>
                  <CardContent>
                    <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm">
                      <code>{template}</code>
                    </pre>
                  </CardContent>
                </Card>
              </TabsContent>
            ))}
          </Tabs>
        </div>
      </section>

    </div>
  );
};
