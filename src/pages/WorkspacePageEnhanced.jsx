import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { ThreeViewer } from '@/components/ThreeViewer';
import { useAuth } from '@/contexts/AuthContext';
import { Switch } from '@/components/ui/switch';
import { projectsAPI, chatAPI, modelsAPI, cadAPI, getData, postData, putData, deleteData } from '@/api';
import { 
  Save, 
  Download, 
  Plus, 
  MessageSquare, 
  Send, 
  Settings,
  PanelLeftClose,
  PanelLeftOpen,
  PanelRightClose,
  PanelRightOpen,
  Home,
  RotateCcw,
  ZoomIn,
  LogOut,
  MoreVertical,
  Edit,
  Trash2,
  RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';

// Sample data
const engines = [
  { value: 'freecad', label: 'FreeCAD (Python)' },
  { value: 'cadquery', label: 'CadQuery (Python)' },
  { value: 'openscad', label: 'OpenSCAD' },
  { value: 'jscad', label: 'JSCAD (JavaScript)' }
];

const materials = [
  { value: 'pla', label: 'PLA Plastic', color: '#2563eb', metalness: 0.1, roughness: 0.7 },
  { value: 'abs', label: 'ABS Plastic', color: '#64748b', metalness: 0.2, roughness: 0.6 },
  { value: 'aluminum', label: 'Aluminum', color: '#b0b8c4', metalness: 0.9, roughness: 0.12, textureUrl: '/textures/metal_brushed.jpg' },
  { value: 'steel', label: 'Steel', color: '#8a99a8', metalness: 0.85, roughness: 0.18, textureUrl: '/textures/metal_brushed.jpg' },
  { value: 'brass', label: 'Brass', color: '#cfa33a', metalness: 0.85, roughness: 0.28, textureUrl: '/textures/metal_polished.jpg' },
  { value: 'copper', label: 'Copper', color: '#b87333', metalness: 0.9, roughness: 0.25, textureUrl: '/textures/metal_brushed.jpg' },
  { value: 'wood', label: 'Wood', color: '#b08968', metalness: 0.0, roughness: 0.9, textureUrl: '/textures/wood_oak.jpg' },
  { value: 'carbon', label: 'Carbon Fiber', color: '#1f2937', metalness: 0.3, roughness: 0.4, textureUrl: '/textures/carbon_fiber.jpg' }
];

const finishes = [
  { value: 'matte', label: 'Matte', roughness: 0.8 },
  { value: 'satin', label: 'Satin', roughness: 0.4 },
  { value: 'polished', label: 'Polished', roughness: 0.1 },
  { value: 'brushed', label: 'Brushed', roughness: 0.3 }
];

const WorkspacePageEnhanced = () => {
  const { projectId } = useParams();
  const { user, logout, isLoading } = useAuth();
  const navigate = useNavigate();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !user) {
      console.log('User not authenticated, redirecting to login');
      navigate('/');
    }
  }, [user, isLoading, navigate]);
  
  // UI State
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const [chatVisible, setChatVisible] = useState(true);
  const [inspectorVisible, setInspectorVisible] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isGeneratingModel, setIsGeneratingModel] = useState(false);
  
  // Project Data
  const [projects, setProjects] = useState([]);
  const [currentProject, setCurrentProject] = useState(null);
  const [selectedMaterial, setSelectedMaterial] = useState(materials[0].value);
  const [selectedFinish, setSelectedFinish] = useState(finishes[0].value);
  const [projectCounter, setProjectCounter] = useState(1);
  
  // Chat State
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [autoScrollChat, setAutoScrollChat] = useState(true);
  const chatEndRef = useRef(null);
  // History of generated parts
  const [historyItems, setHistoryItems] = useState([]);
  
  // Project management state
  const [editingProject, setEditingProject] = useState(null);
  const [editingName, setEditingName] = useState('');

  // Load projects from backend
  useEffect(() => {
    const loadProjects = async () => {
      try {
        // Backend collection route is "/projects"; remove trailing slash to match backend route
        const projectsResponse = await getData('/projects');
        
        // Handle both array format and object format with value property
        const projectsData = Array.isArray(projectsResponse) ? projectsResponse : (projectsResponse.value || projectsResponse);
        console.log('📁 Loaded', projectsData?.length || 0, 'projects');
        
        if (projectsData && projectsData.length > 0) {
          setProjects(projectsData);
          if (projectId) {
            const project = projectsData.find((p) => p.id === projectId);
            if (project) {
              setCurrentProject(project);
              // Chat history will be loaded by the useEffect hook
            } else {
              // If specific project not found, don't override current project
              if (!currentProject) {
                setCurrentProject(projectsData[0]);
              }
            }
          } else {
            // Only set first project if no current project exists
            if (!currentProject) {
              setCurrentProject(projectsData[0]);
            }
          }
        } else {
          setProjects([]);
          setCurrentProject(null);
          setMessages([]);
        }
      } catch (error) {
        console.error('Failed to load projects:', error);
        toast.error('Failed to load projects. Please try logging in again.');
        setProjects([]);
        setCurrentProject(null);
        setMessages([]);
      }
    };
    
    // Only load projects if user is authenticated and we don't have projects yet
    if (user && projects.length === 0) {
      loadProjects();
    }
  }, [user]); // Removed projectId and currentProject from dependencies to prevent re-loading

  // Auto-refresh model when project changes
  useEffect(() => {
    if (currentProject && currentProject.id && !currentProject.id.startsWith('demo-project-')) {
      // Small delay to let the viewer initialize, then fetch S3 URL for existing models
      setTimeout(() => {
        fetchS3ModelUrl(currentProject.id);
      }, 1000);
    }
  }, [currentProject?.id]);

  // Handle new project creation
  const handleNewProject = async () => {
    try {
      const projectData = {
        name: `Project ${projectCounter}`,
        description: 'A new CAD project',
        engine: 'freecad',
        parameters: { width: 50, height: 30, depth: 20, thickness: 2 }
      };
      // Backend expects POST to "/projects/"
      const newProject = await postData('/projects/', projectData);
      console.log('✅ Project created successfully:', newProject.name);
      
      // Add the new project to the existing list immediately
      setProjects(prev => [newProject, ...prev]);
      setCurrentProject(newProject);
      setMessages([]);
      setProjectCounter(prev => prev + 1);
      toast.success('New project created!');
      
      // Navigate to the new project (optional, can be removed if causing issues)
      // navigate(`/workspace/${newProject.id}`);
    } catch (error) {
      console.error('Failed to create project:', error);
      toast.error('Failed to create project');
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isGenerating || !currentProject) {
      return;
    }

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    const messageText = inputMessage;
    setInputMessage('');
    setIsGenerating(true);

    try {
      // Send message to AI service via chat API
      const response = await chatAPI.sendMessage(currentProject.id, messageText);
      
      // Extract data from axios response
      const responseData = response.data || response;
      console.log('✅ AI response received for:', messageText.substring(0, 50) + '...');
      
      const aiResponse = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: responseData.message?.content || responseData.response || 'Generated response',
        code: responseData.code_generated || responseData.generated_code,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, aiResponse]);
      
      // If code was generated, refresh the model after processing time
      if (responseData.code_generated || responseData.generated_code) {
        toast.success('CAD code generated successfully! Processing...');
        
        // Refresh model after processing delays
        setTimeout(() => {
          if (currentProject?.id) {
            fetchS3ModelUrl(currentProject.id);
          }
        }, 10000); // Wait 10 seconds for processing
        
        // Auto-refresh again after 30 seconds
        setTimeout(() => {
          if (currentProject?.id) {
            fetchS3ModelUrl(currentProject.id);
          }
        }, 30000);
      } else {
        toast.success('Message sent successfully!');
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      // Fallback response
      const fallbackResponse = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I apologize, but I encountered an error processing your message. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, fallbackResponse]);
      toast.error('Failed to send message');
    } finally {
      setIsGenerating(false);
    }
  };

  // Auto-scroll chat when new messages arrive
  useEffect(() => {
    if (autoScrollChat && chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isGenerating, autoScrollChat]);

  // Load chat history when current project changes
  useEffect(() => {
    const loadChatHistory = async () => {
      if (currentProject?.id && !currentProject.id.startsWith('demo-project-')) {
        try {
          console.log(`🔄 Loading chat history for project: ${currentProject.id}`);
          const chatHistory = await getData(`/projects/${currentProject.id}/chat`);
          console.log(`✅ Chat history loaded:`, chatHistory);
          setMessages(chatHistory || []);
        } catch (error) {
          console.error('❌ Failed to load chat history:', error);
          setMessages([]);
        }
      } else if (currentProject?.id?.startsWith('demo-project-')) {
        // For demo projects, don't clear existing messages
        console.log(`🔍 Demo project detected, keeping existing messages`);
      }
    };

    loadChatHistory();
  }, [currentProject?.id]);

  const handleExport = async (format) => {
    if (!currentProject) {
      toast.error('No project selected for export');
      return;
    }

    const projectId = currentProject.id;
    const token = localStorage.getItem('cadscribe_token');
    
    if (!token) {
      toast.error('Authentication required');
      return;
    }

    try {
      toast.loading(`Downloading ${format.toUpperCase()} file...`);
      
      // Get download URL from backend
      const response = await fetch(`/api/projects/${encodeURIComponent(projectId)}/download/${format.toUpperCase()}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log(`📡 Export API response status for ${format}: ${response.status}`);
      
      if (response.ok) {
        const contentType = response.headers.get('content-type');
        
        if (!contentType || !contentType.includes('application/json')) {
          const htmlText = await response.text();
          console.error(`❌ Expected JSON but got HTML response:`, htmlText.substring(0, 200));
          toast.error('Backend returned HTML instead of JSON. Check if backend is running correctly.');
          return;
        }
        
        const data = await response.json();
        console.log(`📁 Export API response data for ${format}:`, data);
        
        if (data.success && data.download_url) {
          console.log(`✅ Got S3 URL for ${format}: ${data.download_url}`);
          
          // Download the file directly from S3
          const filename = `${currentProject.name || 'model'}_${Date.now()}.${format.toLowerCase()}`;
          
          // Create a temporary link to download the file
          const link = document.createElement('a');
          link.href = data.download_url;
          link.download = filename;
          link.target = '_blank'; // Open in new tab if direct download fails
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          
          toast.success(`${format.toUpperCase()} file download started!`);
        } else {
          console.log(`⚠️ No ${format} file found for project ${projectId}:`, data);
          toast.info(`No ${format.toUpperCase()} file available yet. The EC2 worker may still be processing the script.`);
        }
      } else {
        console.error(`❌ Failed to get ${format} download URL: ${response.status} ${response.statusText}`);
        const errorText = await response.text();
        console.error('Error response body:', errorText);
        toast.error(`Failed to get ${format.toUpperCase()} download URL`);
      }
    } catch (error) {
      console.error(`Export error for ${format}:`, error);
      toast.error(`Failed to export ${format.toUpperCase()} file: ${error.message}`);
    }
  };

  const handleViewReset = () => {
    toast.info('View reset to default position');
  };

  const renderProjectSidebar = () => (
    <div className="workspace-sidebar h-full flex flex-col">
      {/* Header with CADSCRIBE and Close Button */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between mb-4">
          <Link to="/" className="flex items-center space-x-2">
            <Home className="h-5 w-5 text-primary" />
            <span className="font-bold text-lg text-primary">CADSCRIBE</span>
          </Link>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarVisible(false)}
            className="h-8 w-8 p-0"
          >
            <PanelLeftClose className="h-4 w-4" />
          </Button>
        </div>
        
        <Button size="sm" variant="default" className="w-full" onClick={handleNewProject}>
          <Plus className="h-4 w-4 mr-2" />
          New Project
        </Button>
      </div>
      
      {/* Projects List */}
      <div className="p-4 border-b border-border">
        <h3 className="font-medium text-sm text-muted-foreground mb-3">Projects</h3>
      </div>
      
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-3">
          {projects.map((project) => (
            <Card 
              key={project.id} 
              className={`transition-colors hover:bg-muted/50 ${
                currentProject?.id === project.id ? 'ring-2 ring-primary bg-muted/30' : ''
              }`}
            >
              <CardHeader className="p-3">
                <div className="flex items-start justify-between">
                  <div 
                    className="flex-1 cursor-pointer"
                    onClick={() => {
                      if (editingProject !== project.id) {
                        setCurrentProject(project);
                        setMessages(project.messages || []);
                      }
                    }}
                  >
                    {editingProject === project.id ? (
                      <div className="flex items-center gap-2">
                        <Input
                          value={editingName}
                          onChange={(e) => setEditingName(e.target.value)}
                          onKeyPress={(e) => {
                            if (e.key === 'Enter') {
                              handleRenameProject(project);
                            } else if (e.key === 'Escape') {
                              setEditingProject(null);
                              setEditingName('');
                            }
                          }}
                          onBlur={() => handleRenameProject(project)}
                          className="text-sm h-6 px-2"
                          autoFocus
                        />
                      </div>
                    ) : (
                      <CardTitle className="text-sm">{project.name || project.title}</CardTitle>
                    )}
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="secondary">{project.engine || project.metadata?.engine}</Badge>
                      <span className="text-xs text-muted-foreground">{project.lastModified}</span>
                    </div>
                  </div>
                  
                  {/* 3-dot menu */}
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0 hover:bg-muted"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <MoreVertical className="h-3 w-3" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-40">
                      <DropdownMenuItem
                        onClick={(e) => {
                          e.stopPropagation();
                          startEditingProject(project);
                        }}
                        disabled={project.id.startsWith('demo-project-')}
                      >
                        <Edit className="h-3 w-3 mr-2" />
                        Rename
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteProject(project);
                        }}
                        disabled={project.id.startsWith('demo-project-')}
                        className="text-destructive focus:text-destructive"
                      >
                        <Trash2 className="h-3 w-3 mr-2" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </CardHeader>
            </Card>
          ))}
        </div>
      </ScrollArea>
      
      {/* Bottom Actions */}
      <div className="mt-auto p-4 border-t border-border">
        {/* User Info */}
        <div className="mb-4 text-xs text-muted-foreground">
          <div className="font-medium text-foreground">{user?.name || 'User'}</div>
          <div className="text-muted-foreground">{user?.email || 'user@example.com'}</div>
        </div>
        
        {/* Action Buttons */}
        <div className="space-y-2">
          <Button 
            variant="ghost" 
            size="sm"
            className="w-full justify-start text-foreground hover:bg-muted/50 h-9"
            asChild
          >
            <Link to="/profile">
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </Link>
          </Button>
          
          <Button 
            variant="ghost" 
            size="sm"
            className="w-full justify-start text-foreground hover:bg-muted/50 h-9"
            onClick={() => {
              logout();
              toast.success('Logged out successfully!');
            }}
          >
            <LogOut className="h-4 w-4 mr-2" />
            Logout
          </Button>
        </div>
      </div>
    </div>
  );

  const renderChatSection = () => (
    <div className="workspace-chat h-full flex flex-col">
      {/* Header with Chat Title and Close Button */}
      <div className="p-4 border-b border-border shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <MessageSquare className="h-5 w-5 text-primary" />
            <h3 className="font-semibold">Project Chat</h3>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setChatVisible(false)}
            className="h-8 w-8 p-0"
          >
            <PanelRightClose className="h-4 w-4" />
          </Button>
        </div>
      </div>
      
      {/* Engine Selector */}
      <div className="p-4 border-b border-border shrink-0">
        <Label className="text-xs text-muted-foreground">CAD Engine</Label>
        <Select defaultValue="freecad">
          <SelectTrigger className="mt-1">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {engines.map((engine) => (
              <SelectItem key={engine.value} value={engine.value}>
                {engine.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      
      {/* Auto-scroll toggle */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-border shrink-0">
        <div className="text-xs text-muted-foreground">Auto-scroll</div>
        <Switch checked={autoScrollChat} onCheckedChange={setAutoScrollChat} />
      </div>
      
      {/* Chat Messages - Fixed height with scroll */}
      <div className="flex-1 min-h-0 overflow-hidden">
        <ScrollArea className="h-full p-4">
          <div className="space-y-4">
            {messages && messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 text-sm ${
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted text-foreground'
                  }`}
                >
                  {message.content}
                </div>
              </div>
            ))}
            {isGenerating && (
              <div className="flex justify-start">
                <div className="bg-muted rounded-lg p-3 text-sm text-foreground">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full"></div>
                    <span>Generating...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
        </ScrollArea>
      </div>
      
      {/* Chat Input - Fixed at bottom */}
      <div className="p-4 border-t border-border shrink-0">
        <div className="flex space-x-2">
          <Input
            placeholder="Describe your changes..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            disabled={isGenerating}
          />
          <Button 
            size="sm" 
            onClick={handleSendMessage}
            disabled={isGenerating}
            variant="default"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );

  const renderInspector = () => (
    <div className="workspace-inspector">
      <Tabs defaultValue="material" className="h-full flex flex-col">
        {/* Header with Tabs and Close Button */}
        <div className="p-4 border-b border-border">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold">Inspector</h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setInspectorVisible(false)}
              className="h-8 w-8 p-0"
            >
              <PanelRightClose className="h-4 w-4" />
            </Button>
          </div>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="material">Material</TabsTrigger>
            <TabsTrigger value="export">Export</TabsTrigger>
          </TabsList>
        </div>
        
        <div className="flex-1 overflow-y-auto">
          <TabsContent value="material" className="p-4 space-y-4 m-0">
            <div>
              <h3 className="font-semibold mb-3">Material Properties</h3>
              
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="material">Material Type</Label>
                  <Select value={selectedMaterial} onValueChange={setSelectedMaterial}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {materials.map((material) => (
                        <SelectItem key={material.value} value={material.value}>
                          {material.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="finish">Surface Finish</Label>
                  <Select value={selectedFinish} onValueChange={setSelectedFinish}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {finishes.map((finish) => (
                        <SelectItem key={finish.value} value={finish.value}>
                          {finish.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="p-3 bg-muted rounded-lg">
                  <div className="text-sm space-y-1">
                    <div>Color: <Badge variant="secondary">{getCurrentMaterial().color}</Badge></div>
                    <div>Metalness: {(getCurrentMaterial().metalness * 100).toFixed(0)}%</div>
                    <div>Roughness: {(getCurrentMaterial().roughness * 100).toFixed(0)}%</div>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="export" className="p-4 space-y-4 m-0">
            <div>
              <h3 className="font-semibold mb-3">Export Options</h3>
              
              <div className="space-y-3">
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => handleExport('stl')}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export STL
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => handleExport('step')}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export STEP
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => handleExport('iges')}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export IGES
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => handleExport('obj')}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export OBJ
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => handleExport('fcstd')}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export FCSTD
                </Button>
              </div>
            </div>
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );

  const getCurrentMaterial = () => {
    const material = materials.find(m => m.value === selectedMaterial);
    const finish = finishes.find(f => f.value === selectedFinish);
    
    if (!material || !finish) return materials[0];
    
    return {
      ...material,
      roughness: finish.roughness
    };
  };


  // State for output files
  const [outputFiles, setOutputFiles] = useState({});
  const [loadingOutputs, setLoadingOutputs] = useState({});
  const [viewerRefreshKey, setViewerRefreshKey] = useState(0);
  const [s3ModelUrls, setS3ModelUrls] = useState({}); // Cache for actual S3 URLs

  // Helper function to get correct model URL
  const getModelUrl = (projectId) => {
    if (projectId === "demo-project-1") {
      return "/files/placeholder_cube.stl";
    } else if (projectId === "demo-project-2") {
      return "/files/placeholder_flange.stl";
    }
    
    // For regular projects, check if we have cached S3 URL
    if (projectId && !projectId.startsWith('demo-project-')) {
      const cachedUrl = s3ModelUrls[projectId];
      if (cachedUrl) {
        console.log(`🎯 Using cached S3 URL for ${projectId}: ${cachedUrl}`);
        return cachedUrl;
      }
    }
    
    // Final fallback to placeholder
    return `/files/placeholder_cube.stl`;
  };

  // Fetch actual S3 URL for the model with format priority
  const fetchS3ModelUrl = async (projectId) => {
    if (!projectId || projectId.startsWith('demo-project-')) {
      return;
    }
    
    console.log(`🔄 Fetching S3 URL for project: ${projectId}`);
    setLoadingOutputs(prev => ({ ...prev, [projectId]: true }));
    
    // Check token before making request (use correct token key)
    const token = localStorage.getItem('cadscribe_token');
    console.log(`🔑 Token available: ${!!token}, length: ${token?.length || 0}`);
    console.log(`🔍 Checking localStorage keys:`, Object.keys(localStorage));
    
    if (!token) {
      console.error('❌ No JWT token found in localStorage');
      toast.error('Authentication required. Please log in to access 3D models.');
      
      // Check if user context is available
      if (!user) {
        console.log('🔄 User not authenticated, redirecting to login...');
        // The AuthContext should handle this automatically
      }
      return;
    }
    
    // Priority order: STEP > IGES > FCSTD > STL > OBJ (assembled formats first)
    const formatPriority = ['STEP', 'IGES', 'FCSTD', 'STL', 'OBJ'];
    
    for (const format of formatPriority) {
      try {
        console.log(`🔍 Trying format: ${format} for project ${projectId}`);
        
        const response = await fetch(`/api/projects/${encodeURIComponent(projectId)}/download/${format}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        console.log(`📡 ${format} API response status: ${response.status}`);
        
        if (response.ok) {
          // Check if response is actually JSON
          const contentType = response.headers.get('content-type');
          console.log(`📋 Response content-type: ${contentType}`);
          
          if (!contentType || !contentType.includes('application/json')) {
            console.log(`⚠️ ${format} returned non-JSON response, trying next format...`);
            continue; // Try next format
          }
          
          const data = await response.json();
          console.log(`📁 ${format} API response data:`, data);
          
          if (data.success && data.download_url) {
            console.log(`✅ Got ${format} S3 URL for ${projectId}: ${data.download_url}`);
            
            // Cache the S3 URL
            setS3ModelUrls(prev => ({
              ...prev,
              [projectId]: data.download_url
            }));
            
            // Force ThreeViewer to reload with new URL
            setViewerRefreshKey(prev => prev + 1);
            
            toast.success(`3D model loaded successfully! (${format} format)`);
            setLoadingOutputs(prev => ({ ...prev, [projectId]: false }));
            return; // Success! Exit the format loop
          } else {
            console.log(`⚠️ No ${format} file found for project ${projectId}, trying next format...`);
            continue; // Try next format
          }
        } else {
          console.log(`❌ ${format} request failed (${response.status}), trying next format...`);
          continue; // Try next format
        }
      } catch (formatError) {
        console.log(`❌ Error trying ${format}: ${formatError.message}, trying next format...`);
        continue; // Try next format
      }
    }
    
    // If we get here, no format worked
    console.log(`⚠️ No supported file formats found for project ${projectId}`);
    toast.info('No 3D model files available yet. The EC2 worker may still be processing the script.');
    setLoadingOutputs(prev => ({ ...prev, [projectId]: false }));
  };

  // Check processing status
  const checkProcessingStatus = async (projectId) => {
    try {
      const response = await fetch(`/api/projects/${encodeURIComponent(projectId)}/status`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('cadscribe_token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log(`📊 Processing status for ${projectId}:`, data);
        
        if (data.status_info?.output_files_available) {
          toast.success('Output files are ready! Fetching 3D model...');
          fetchS3ModelUrl(projectId);
        } else {
          toast.info(`Status: ${data.status_info?.message || 'Processing...'}`);
        }
      }
    } catch (error) {
      console.error('Error checking status:', error);
    }
  };

  // Test backend connectivity
  const testBackendConnection = async () => {
    try {
      console.log('🧪 Testing backend connection...');
      const response = await fetch('/api/projects/test');
      const data = await response.json();
      console.log('✅ Backend test successful:', data);
      toast.success('Backend connection verified!');
    } catch (error) {
      console.error('❌ Backend test failed:', error);
      toast.error('Backend connection failed!');
    }
  };

  // Test debug endpoint
  const testDebugEndpoint = async (projectId) => {
    try {
      console.log(`🧪 Testing debug endpoint for project: ${projectId}`);
      const response = await fetch(`/api/projects/${encodeURIComponent(projectId)}/debug`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('cadscribe_token')}`
        }
      });
      const data = await response.json();
      console.log('🔍 Debug endpoint response:', data);
      
      if (data.success) {
        toast.success(`Debug: Found ${data.output_files_count} files, S3: ${data.s3_configured}`);
      } else {
        toast.error(`Debug failed: ${data.error}`);
      }
    } catch (error) {
      console.error('❌ Debug endpoint failed:', error);
      toast.error('Debug endpoint failed');
    }
  };

  // Simple refresh function
  const refreshModel = (projectId) => {
    // First test backend connection
    testBackendConnection();
    // Test debug endpoint
    testDebugEndpoint(projectId);
    // Then check status, then try to fetch model
    checkProcessingStatus(projectId);
    fetchS3ModelUrl(projectId);
  };

  // Handle project rename
  const handleRenameProject = async (project) => {
    if (!editingName.trim()) {
      toast.error('Project name cannot be empty');
      return;
    }

    try {
      // Call backend API to rename project
      const updatedProject = await putData(`/projects/${project.id}`, { 
        name: editingName,
        description: project.description,
        engine: project.engine || project.metadata?.engine,
        parameters: project.parameters || project.metadata?.parameters || {}
      });
      
      // Update local state
      const updatedProjects = projects.map(p => 
        p.id === project.id 
          ? { ...p, ...updatedProject, title: editingName, name: editingName }
          : p
      );
      setProjects(updatedProjects);
      
      if (currentProject?.id === project.id) {
        setCurrentProject({ ...currentProject, ...updatedProject, title: editingName, name: editingName });
      }
      
      setEditingProject(null);
      setEditingName('');
      toast.success('Project renamed successfully!');
    } catch (error) {
      console.error('Failed to rename project:', error);
      toast.error('Failed to rename project');
      // Reset editing state on error
      setEditingProject(null);
      setEditingName('');
    }
  };

  // Handle project delete
  const handleDeleteProject = async (project) => {
    if (project.id.startsWith('demo-project-')) {
      toast.error('Cannot delete demo projects');
      return;
    }

    if (!confirm(`Are you sure you want to delete "${project.name || project.title}"?`)) {
      return;
    }

    try {
      // Call backend API to delete project
      await deleteData(`/projects/${project.id}`);
      
      // Update local state
      const updatedProjects = projects.filter(p => p.id !== project.id);
      setProjects(updatedProjects);
      
      if (currentProject?.id === project.id) {
        setCurrentProject(updatedProjects.length > 0 ? updatedProjects[0] : null);
        setMessages([]);
      }
      
      toast.success('Project deleted successfully!');
    } catch (error) {
      console.error('Failed to delete project:', error);
      toast.error('Failed to delete project');
    }
  };

  // Start editing project name
  const startEditingProject = (project) => {
    setEditingProject(project.id);
    setEditingName(project.name || project.title || '');
  };

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render if not authenticated (will redirect)
  if (!user) {
    return null;
  }

  if (isFullscreen) {
    return (
      <div className="fixed inset-0 z-50 bg-background">
        <ThreeViewer
          key={`viewer-${currentProject?.id}-${viewerRefreshKey}`}
          modelUrl={currentProject ? getModelUrl(currentProject.id) : undefined}
          projectId={currentProject?.id}
          material={getCurrentMaterial()}
          className="w-full h-full"
          onFullscreen={setIsFullscreen}
        />
      </div>
    );
  }

  return (
    <div className="workspace-layout h-screen overflow-hidden">
      {/* Project Sidebar */}
      {sidebarVisible && (
        <div className="transition-all duration-300 ease-out">{renderProjectSidebar()}</div>
      )}
      
      {/* Chat Section */}
      {chatVisible && (
        <div className="transition-all duration-300 ease-out">{renderChatSection()}</div>
      )}
      
      {/* Main Viewer */}
      <div className="workspace-viewer">
        {/* Header Toolbar */}
        <div className="flex items-center justify-between p-4 border-b border-border bg-background">
          <div className="flex items-center space-x-2">
            {!sidebarVisible && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setSidebarVisible(true)}
                title="Show Project Sidebar"
              >
                <PanelLeftOpen className="h-4 w-4" />
              </Button>
            )}
            {!chatVisible && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setChatVisible(true)}
                title="Show Project Chat"
              >
                <MessageSquare className="h-4 w-4" />
              </Button>
            )}
            {!inspectorVisible && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setInspectorVisible(true)}
                title="Show Inspector"
              >
                <PanelRightOpen className="h-4 w-4" />
              </Button>
            )}
            <h1 className="text-lg font-semibold">
              {currentProject?.name || currentProject?.title || 'Select a Project'}
            </h1>
            
            {/* Refresh 3D Model Button */}
            {currentProject && !currentProject.id.startsWith('demo-project-') && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => refreshModel(currentProject.id)}
                disabled={loadingOutputs[currentProject.id]}
                title="Refresh 3D Model from S3"
                className="ml-2"
              >
                <RefreshCw className={`h-4 w-4 ${loadingOutputs[currentProject.id] ? 'animate-spin' : ''}`} />
                <span className="ml-1">Refresh Model</span>
              </Button>
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => toast.success('Project saved!')}
            >
              <Save className="h-4 w-4 mr-2" />
              Save
            </Button>
          </div>
        </div>
        
        {/* 3D Viewer */}
        <div className="flex-1">
          <ThreeViewer
            key={`viewer-${currentProject?.id}-${viewerRefreshKey}`}
            modelUrl={currentProject ? getModelUrl(currentProject.id) : undefined}
            projectId={currentProject?.id}
            material={getCurrentMaterial()}
            className="w-full h-full"
            onFullscreen={setIsFullscreen}
          />
        </div>

        {/* Mobile History (bottom on mobile) */}
        <div className="md:hidden p-4 border-t border-border bg-background">
          <ScrollArea className="max-h-48">
            <div className="max-w-3xl mx-auto">
              <h3 className="font-semibold mb-2">Recent Parts</h3>
              {historyItems.length === 0 ? (
                <div className="text-sm text-muted-foreground">No history yet. Generate a part to see it here.</div>
              ) : (
                <div className="space-y-2">
                  {historyItems.map(item => (
                    <Card key={item.id} className="p-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium">{item.title}</div>
                          <div className="text-xs text-muted-foreground">{new Date(item.timestamp).toLocaleString()}</div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button size="sm" variant="outline" onClick={() => handleExport('stl')}>STL</Button>
                          <Button size="sm" variant="outline" onClick={() => handleExport('step')}>STEP</Button>
                          <Button size="sm" variant="outline" onClick={() => handleExport('iges')}>IGES</Button>
                          <Button size="sm" variant="outline" onClick={() => handleExport('obj')}>OBJ</Button>
                          <Button size="sm" variant="outline" onClick={() => handleExport('fcstd')}>FCSTD</Button>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </ScrollArea>
        </div>
      </div>
      
      {/* Inspector Panel */}
      {inspectorVisible && (
        <div className="transition-all duration-300 ease-out">{renderInspector()}</div>
      )}
      
    </div>
  );
};

export default WorkspacePageEnhanced;