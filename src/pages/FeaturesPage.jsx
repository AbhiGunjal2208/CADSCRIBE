import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Zap, Code, Eye, GitBranch, Download, MessageSquare, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const features = [
  {
    icon: Zap,
    title: "Parametric Templates",
    description: "Create reusable, customizable 3D models with parameters that update in real-time. Perfect for product families and design iterations.",
    benefits: ["Real-time parameter updates", "Reusable design patterns", "Instant model regeneration"],
    category: "Design"
  },
  {
    icon: Code,
    title: "Multi-engine Support", 
    description: "Work with CadQuery, OpenSCAD, FreeCAD, and JSCAD in one unified interface. Switch between engines seamlessly.",
    benefits: ["4 scripting languages", "Unified workflow", "Engine-specific optimizations"],
    category: "Development"
  },
  {
    icon: Eye,
    title: "Live 3D Preview",
    description: "See your 3D models render instantly with our advanced three.js viewer. Rotate, zoom, and inspect every detail.",
    benefits: ["Instant visual feedback", "High-quality rendering", "Interactive navigation"],
    category: "Visualization"
  },
  {
    icon: GitBranch,
    title: "Version Control",
    description: "Track changes and iterations with built-in model versioning. Never lose your design progress again.",
    benefits: ["Automatic versioning", "Change tracking", "Easy rollbacks"],
    category: "Management"
  },
  {
    icon: Download,
    title: "Multiple Export Formats",
    description: "Export to STL, STEP, OBJ and other popular 3D formats. Ready for 3D printing, manufacturing, or further processing.",
    benefits: ["STL for 3D printing", "STEP for CAD", "OBJ for graphics"],
    category: "Export"
  },
  {
    icon: MessageSquare,
    title: "Project Documentation",
    description: "Document your design process with integrated chat history. Keep track of decisions and iterations.",
    benefits: ["Design documentation", "Decision tracking", "Team collaboration"],
    category: "Collaboration"
  }
];

const FeaturesPage = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="section-padding bg-gradient-to-br from-background via-background to-muted">
        <div className="container-main text-center">
          <h1 className="text-4xl sm:text-5xl font-bold text-foreground mb-6">
            Powerful Features for{' '}
            <span className="bg-gradient-hero bg-clip-text text-transparent">
              Modern CAD
            </span>
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            Everything you need to create, iterate, and export parametric 3D models 
            using the power of programming languages.
          </p>
          <Button className="btn-hero" asChild>
            <Link to="/auth/signup">
              Get Started Free
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
      </section>

      {/* Features Grid */}
      <section className="section-padding">
        <div className="container-main">
          <div className="grid lg:grid-cols-2 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="card-feature group">
                <CardHeader>
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-12 h-12 bg-gradient-primary rounded-lg flex items-center justify-center">
                      <feature.icon className="h-6 w-6 text-primary-foreground" />
                    </div>
                    <Badge variant="secondary">{feature.category}</Badge>
                  </div>
                  <CardTitle className="text-xl mb-2">{feature.title}</CardTitle>
                  <CardDescription className="text-base">
                    {feature.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {feature.benefits.map((benefit, idx) => (
                      <li key={idx} className="flex items-center text-sm text-muted-foreground">
                        <div className="w-1.5 h-1.5 bg-primary rounded-full mr-3"></div>
                        {benefit}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Workflow Section */}
      <section className="section-padding bg-muted/30">
        <div className="container-main">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-foreground mb-4">
              Streamlined Workflow
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              From concept to export in minutes, not hours
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-primary rounded-full flex items-center justify-center mx-auto mb-4">
                <Code className="h-8 w-8 text-primary-foreground" />
              </div>
              <h3 className="text-xl font-semibold mb-2">1. Write Code</h3>
              <p className="text-muted-foreground">
                Use your preferred scripting language to define parametric models
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-secondary rounded-full flex items-center justify-center mx-auto mb-4">
                <Eye className="h-8 w-8 text-secondary-foreground" />
              </div>
              <h3 className="text-xl font-semibold mb-2">2. Preview Live</h3>
              <p className="text-muted-foreground">
                See your model render instantly with real-time parameter updates
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-accent rounded-full flex items-center justify-center mx-auto mb-4">
                <Download className="h-8 w-8 text-accent-foreground" />
              </div>
              <h3 className="text-xl font-semibold mb-2">3. Export & Use</h3>
              <p className="text-muted-foreground">
                Export to multiple formats for 3D printing, manufacturing, or CAD
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section-padding bg-gradient-hero">
        <div className="container-main text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-primary-foreground mb-4">
            Ready to Experience the Future of CAD?
          </h2>
          <p className="text-xl text-primary-foreground/90 mb-8 max-w-2xl mx-auto">
            Join the revolution of programmatic design and unlock your creative potential
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              size="lg" 
              variant="secondary"
              className="bg-background text-foreground hover:bg-background/90"
              asChild
            >
              <Link to="/auth/signup">Start Building Now</Link>
            </Button>
            <Button 
              size="lg" 
              variant="outline"
              className="border-primary-foreground text-primary-foreground hover:bg-primary-foreground hover:text-primary"
              asChild
            >
              <Link to="/workspace">View Demo</Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default FeaturesPage;