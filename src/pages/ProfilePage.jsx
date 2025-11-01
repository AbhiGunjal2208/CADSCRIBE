import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import { useTheme } from '@/contexts/ThemeContext';
import { useAuth } from '@/contexts/AuthContext';
import { userAPI, getData, putData } from '@/api';
import { 
  ArrowLeft, 
  Camera, 
  Save, 
  Trash2, 
  Eye, 
  EyeOff, 
  Monitor, 
  Moon, 
  Sun,
  Shield,
  Bell,
  Palette,
  Settings,
  User,
  LogOut
} from 'lucide-react';
import { toast } from 'sonner';

const ProfilePage = () => {
  const { user, logout } = useAuth();
  const { theme, setTheme } = useTheme();
  
  // Profile state
  const [profileData, setProfileData] = useState({
    name: user?.name || 'John Doe',
    email: user?.email || 'john.doe@example.com',
    avatar: user?.avatar || '',
  });
  const [isLoading, setIsLoading] = useState(false);
  
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  
  const [showPassword, setShowPassword] = useState({
    current: false,
    new: false,
    confirm: false,
  });
  
  // Settings state
  const [settings, setSettings] = useState({
    accentColor: 'blue',
    fontSize: 'normal',
    sidebarBehavior: 'visible',
    defaultUnits: 'mm',
    gridVisible: true,
    defaultMaterial: 'plastic',
    defaultExportFormat: 'step',
    emailNotifications: true,
    productUpdates: true,
    twoFactorAuth: false,
  });


  // Track member since date
  const [memberSince, setMemberSince] = useState(null);

  // Load user data from backend
  useEffect(() => {
    const loadUserData = async () => {
      try {
        const data = await getData('/user/profile');
        setProfileData({
          name: data.name || '',
          email: data.email || '',
          avatar: data.avatar || '',
        });
        // Save created_at for Member since
        if (data.created_at) {
          setMemberSince(new Date(data.created_at));
        }
        setSettings(data.settings || settings);
      } catch (err) {
        console.error('Failed to load user profile:', err);
      }
    };
    loadUserData();
  }, [user]);


  const handleProfileUpdate = async () => {
    setIsLoading(true);
    try {
      await putData('/user/profile', profileData);
      toast.success('Profile updated successfully!');
    } catch (error) {
      console.error('Failed to update profile:', error);
      toast.error('Failed to update profile');
    } finally {
      setIsLoading(false);
    }
  };


  const handlePasswordChange = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast.error('New passwords do not match');
      return;
    }
    try {
      // Backend expects snake_case keys: current_password, new_password
      await postData('/user/change-password', {
        current_password: passwordData.currentPassword,
        new_password: passwordData.newPassword,
      });
      toast.success('Password changed successfully!');
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
    } catch (error) {
      console.error('Failed to change password:', error);
      toast.error('Failed to change password');
    }
  };


  const handleSettingsUpdate = async () => {
    try {
      await putData('/user/settings', settings);
      // Apply accent color to CSS variables immediately after saving
      try {
        const root = document.documentElement;
        // Our accentColors are defined as hsl(...). Extract the inside and set to --primary and --accent
        const selected = accentColors.find(c => c.value === settings.accentColor);
        if (selected && selected.color.startsWith('hsl(')) {
          const hsl = selected.color.slice(4, -1); // remove 'hsl(' and ')'
          root.style.setProperty('--primary', hsl);
          root.style.setProperty('--accent', hsl);
        }
      } catch {}
      toast.success('Settings saved successfully!');
    } catch (error) {
      console.error('Failed to update settings:', error);
      toast.error('Failed to update settings');
    }
  };


  const handleAccountDelete = async () => {
    try {
      await postData('/user/delete', {});
      toast.success('Account deleted successfully!');
      // Ensure user is logged out and redirect to login
      await logout();
      window.location.href = '/auth/login';
    } catch (error) {
      console.error('Failed to delete account:', error);
      toast.error('Failed to delete account');
    }
  };

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully!');
  };

  const accentColors = [
    { value: 'blue', label: 'Blue', color: 'hsl(221, 83%, 53%)' },
    { value: 'orange', label: 'Orange', color: 'hsl(24, 95%, 53%)' },
    { value: 'gray', label: 'Gray', color: 'hsl(215, 25%, 52%)' },
  ];

  const [sessionHistory, setSessionHistory] = useState([]);
  useEffect(() => {
    getData('/user/sessions')
      .then(setSessionHistory)
      .catch((err) => { setSessionHistory([]); console.error('Failed to load sessions', err); });
  }, []);

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation Header */}
      <header className="sticky top-0 z-50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border">
        <div className="container-main">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" asChild>
                <Link to="/workspace" className="flex items-center">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Workspace
                </Link>
              </Button>
              <Separator orientation="vertical" className="h-6" />
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
                  <span className="text-primary-foreground font-bold text-sm">CS</span>
                </div>
                <span className="font-bold text-xl text-foreground">CADSCRIBE</span>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
                className="w-9 h-9 p-0"
              >
                {theme === 'light' ? (
                  <Moon className="h-4 w-4" />
                ) : (
                  <Sun className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container-main py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Profile Section */}
          <div className="lg:col-span-5">
            <Card>
              <CardHeader>
                <div className="flex items-center space-x-2">
                  <User className="h-5 w-5 text-primary" />
                  <CardTitle>Profile</CardTitle>
                </div>
                <CardDescription>
                  Manage your account information and preferences
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Avatar Section */}
                <div className="flex items-center space-x-4">
                  <Avatar className="h-20 w-20">
                    <AvatarImage src={profileData.avatar} alt="Profile" />
                    <AvatarFallback className="text-lg">
                      {profileData.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div className="space-y-2">
                    <Button variant="outline" size="sm" className="flex items-center">
                      <Camera className="h-4 w-4 mr-2" />
                      Change Avatar
                    </Button>
                    <div className="flex items-center space-x-2">
                      <Badge variant="secondary">Free Plan</Badge>
                      <span className="text-sm text-muted-foreground">
                        {memberSince ? `Member since ${memberSince.toLocaleString(undefined, { month: 'short', year: 'numeric' })}` : 'Member since —'}
                      </span>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Basic Info */}
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name</Label>
                    <Input
                      id="name"
                      value={profileData.name}
                      onChange={(e) => setProfileData({ ...profileData, name: e.target.value })}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address</Label>
                    <Input
                      id="email"
                      type="email"
                      value={profileData.email}
                      onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                    />
                  </div>
                </div>

                <Separator />

                {/* Password Change */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium">Change Password</h3>
                  
                  <div className="space-y-2">
                    <Label htmlFor="current-password">Current Password</Label>
                    <div className="relative">
                      <Input
                        id="current-password"
                        type={showPassword.current ? "text" : "password"}
                        value={passwordData.currentPassword}
                        onChange={(e) => setPasswordData({ ...passwordData, currentPassword: e.target.value })}
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                        onClick={() => setShowPassword({ ...showPassword, current: !showPassword.current })}
                      >
                        {showPassword.current ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="new-password">New Password</Label>
                    <div className="relative">
                      <Input
                        id="new-password"
                        type={showPassword.new ? "text" : "password"}
                        value={passwordData.newPassword}
                        onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                        onClick={() => setShowPassword({ ...showPassword, new: !showPassword.new })}
                      >
                        {showPassword.new ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="confirm-password">Confirm New Password</Label>
                    <div className="relative">
                      <Input
                        id="confirm-password"
                        type={showPassword.confirm ? "text" : "password"}
                        value={passwordData.confirmPassword}
                        onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                        onClick={() => setShowPassword({ ...showPassword, confirm: !showPassword.confirm })}
                      >
                        {showPassword.confirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                  </div>
                  
                  <Button onClick={handlePasswordChange} className="w-full">
                    Update Password
                  </Button>
                </div>

                <Separator />

                {/* Account Actions */}
                <div className="space-y-4">
                  <Button onClick={handleProfileUpdate} className="w-full">
                    <Save className="h-4 w-4 mr-2" />
                    Save Profile Changes
                  </Button>
                  
                  <Button onClick={handleLogout} variant="outline" className="w-full">
                    <LogOut className="h-4 w-4 mr-2" />
                    Logout
                  </Button>
                  
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant="destructive" className="w-full">
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete Account
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                        <AlertDialogDescription>
                          This action cannot be undone. This will permanently delete your account
                          and remove all your data from our servers.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction onClick={handleAccountDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                          Delete Account
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Settings Section */}
          <div className="lg:col-span-7">
            <Card>
              <CardHeader>
                <div className="flex items-center space-x-2">
                  <Settings className="h-5 w-5 text-primary" />
                  <CardTitle>Settings</CardTitle>
                </div>
                <CardDescription>
                  Configure your workspace and application preferences
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="ui" className="w-full">
                  <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="ui" className="flex items-center gap-2">
                      <Palette className="h-4 w-4" />
                      UI
                    </TabsTrigger>
                    <TabsTrigger value="workspace" className="flex items-center gap-2">
                      <Monitor className="h-4 w-4" />
                      Workspace
                    </TabsTrigger>
                    <TabsTrigger value="notifications" className="flex items-center gap-2">
                      <Bell className="h-4 w-4" />
                      Notifications
                    </TabsTrigger>
                    <TabsTrigger value="security" className="flex items-center gap-2">
                      <Shield className="h-4 w-4" />
                      Security
                    </TabsTrigger>
                  </TabsList>

                  <TabsContent value="ui" className="space-y-6 mt-6">
                    <div className="space-y-4">
                      <h3 className="text-lg font-medium">Theme & UI Preferences</h3>
                      
                      <div className="space-y-3">
                        <Label>Theme</Label>
                        <div className="flex space-x-2">
                          <Button
                            variant={theme === 'light' ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setTheme('light')}
                            className="flex items-center"
                          >
                            <Sun className="h-4 w-4 mr-2" />
                            Light
                          </Button>
                          <Button
                            variant={theme === 'dark' ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setTheme('dark')}
                            className="flex items-center"
                          >
                            <Moon className="h-4 w-4 mr-2" />
                            Dark
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => window.matchMedia('(prefers-color-scheme: dark)').matches ? setTheme('dark') : setTheme('light')}
                            className="flex items-center"
                          >
                            <Monitor className="h-4 w-4 mr-2" />
                            Auto
                          </Button>
                        </div>
                      </div>

                      <div className="space-y-3">
                        <Label>Accent Color</Label>
                        <div className="flex space-x-2">
                          {accentColors.map((color) => (
                            <Button
                              key={color.value}
                              variant={settings.accentColor === color.value ? 'default' : 'outline'}
                              size="sm"
                              onClick={() => setSettings({ ...settings, accentColor: color.value })}
                              className="flex items-center"
                            >
                              <div 
                                className="w-3 h-3 rounded-full mr-2" 
                                style={{ backgroundColor: color.color }}
                              />
                              {color.label}
                            </Button>
                          ))}
                        </div>
                      </div>

                      <div className="space-y-3">
                        <Label htmlFor="font-size">Font Size</Label>
                        <Select value={settings.fontSize} onValueChange={(value) => setSettings({ ...settings, fontSize: value })}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="small">Small</SelectItem>
                            <SelectItem value="normal">Normal</SelectItem>
                            <SelectItem value="large">Large</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="space-y-0.5">
                          <Label htmlFor="sidebar-behavior">Auto-hide Sidebar</Label>
                          <p className="text-sm text-muted-foreground">Automatically hide sidebar when not in use</p>
                        </div>
                        <Switch
                          id="sidebar-behavior"
                          checked={settings.sidebarBehavior === 'auto-hide'}
                          onCheckedChange={(checked) => 
                            setSettings({ ...settings, sidebarBehavior: checked ? 'auto-hide' : 'visible' })
                          }
                        />
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="workspace" className="space-y-6 mt-6">
                    <div className="space-y-4">
                      <h3 className="text-lg font-medium">Workspace Defaults</h3>
                      
                      <div className="space-y-3">
                        <Label htmlFor="default-units">Default Units</Label>
                        <Select value={settings.defaultUnits} onValueChange={(value) => setSettings({ ...settings, defaultUnits: value })}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="mm">Millimeters (mm)</SelectItem>
                            <SelectItem value="cm">Centimeters (cm)</SelectItem>
                            <SelectItem value="m">Meters (m)</SelectItem>
                            <SelectItem value="in">Inches (in)</SelectItem>
                            <SelectItem value="ft">Feet (ft)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="space-y-0.5">
                          <Label htmlFor="grid-visible">Show Grid by Default</Label>
                          <p className="text-sm text-muted-foreground">Display reference grid in 3D viewer</p>
                        </div>
                        <Switch
                          id="grid-visible"
                          checked={settings.gridVisible}
                          onCheckedChange={(checked) => setSettings({ ...settings, gridVisible: checked })}
                        />
                      </div>

                      <div className="space-y-3">
                        <Label htmlFor="default-material">Default Material</Label>
                        <Select value={settings.defaultMaterial} onValueChange={(value) => setSettings({ ...settings, defaultMaterial: value })}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="plastic">Plastic (PLA)</SelectItem>
                            <SelectItem value="abs">ABS Plastic</SelectItem>
                            <SelectItem value="aluminum">Aluminum</SelectItem>
                            <SelectItem value="steel">Steel</SelectItem>
                            <SelectItem value="wood">Wood</SelectItem>
                            <SelectItem value="resin">Resin</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-3">
                        <Label htmlFor="default-export">Default Export Format</Label>
                        <Select value={settings.defaultExportFormat} onValueChange={(value) => setSettings({ ...settings, defaultExportFormat: value })}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="step">STEP (.step)</SelectItem>
                            <SelectItem value="stl">STL (.stl)</SelectItem>
                            <SelectItem value="obj">OBJ (.obj)</SelectItem>
                            <SelectItem value="gltf">glTF (.gltf)</SelectItem>
                            <SelectItem value="3mf">3MF (.3mf)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="notifications" className="space-y-6 mt-6">
                    <div className="space-y-4">
                      <h3 className="text-lg font-medium">Notification Preferences</h3>
                      
                      <div className="flex items-center justify-between">
                        <div className="space-y-0.5">
                          <Label htmlFor="email-notifications">Email Notifications</Label>
                          <p className="text-sm text-muted-foreground">Receive updates about your projects via email</p>
                        </div>
                        <Switch
                          id="email-notifications"
                          checked={settings.emailNotifications}
                          onCheckedChange={(checked) => setSettings({ ...settings, emailNotifications: checked })}
                        />
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="space-y-0.5">
                          <Label htmlFor="product-updates">Product Updates</Label>
                          <p className="text-sm text-muted-foreground">Get notified about new features and improvements</p>
                        </div>
                        <Switch
                          id="product-updates"
                          checked={settings.productUpdates}
                          onCheckedChange={(checked) => setSettings({ ...settings, productUpdates: checked })}
                        />
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="security" className="space-y-6 mt-6">
                    <div className="space-y-4">
                      <h3 className="text-lg font-medium">Security Settings</h3>
                      
                      <div className="flex items-center justify-between">
                        <div className="space-y-0.5">
                          <Label htmlFor="two-factor">Two-Factor Authentication</Label>
                          <p className="text-sm text-muted-foreground">Add an extra layer of security to your account</p>
                        </div>
                        <Switch
                          id="two-factor"
                          checked={settings.twoFactorAuth}
                          onCheckedChange={(checked) => setSettings({ ...settings, twoFactorAuth: checked })}
                        />
                      </div>

                      <Separator />

                      <div className="space-y-4">
                        <h4 className="font-medium">Recent Sessions</h4>
                        <div className="space-y-3">
                          {sessionHistory.map((session, index) => (
                            <div key={index} className="flex items-center justify-between p-3 border border-border rounded-lg">
                              <div>
                                <div className="font-medium text-sm">{session.device}</div>
                                <div className="text-sm text-muted-foreground">{session.location} • {session.lastLogin}</div>
                              </div>
                              <Button variant="outline" size="sm">
                                Revoke
                              </Button>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>

                <Separator className="my-6" />

                <Button onClick={handleSettingsUpdate} className="w-full">
                  <Save className="h-4 w-4 mr-2" />
                  Save All Settings
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
