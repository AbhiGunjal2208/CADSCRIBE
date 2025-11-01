import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
// OpenCascade.js will be loaded dynamically to avoid ESM issues
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { 
  RotateCcw, 
  Grid3X3, 
  Eye, 
  Maximize, 
  ZoomIn, 
  RotateCw, 
  Camera,
  Minimize
} from 'lucide-react';
import { toast } from 'sonner';

export const ThreeViewer = ({ 
  modelUrl = '/files/placeholder_cube.stl', 
  projectId,
  material,
  className = '',
  onFullscreen,
  isFullscreen = false
}) => {
  const containerRef = useRef(null);
  const sceneRef = useRef();
  const rendererRef = useRef();
  const cameraRef = useRef();
  const controlsRef = useRef();
  const modelRef = useRef();
  const animationIdRef = useRef();
  const wireframeMeshRef = useRef();
  
  const [showGrid, setShowGrid] = useState(true);
  const [autoRotate, setAutoRotate] = useState(false);
  const [isVisible, setIsVisible] = useState(true);
  const [showWireframe, setShowWireframe] = useState(true);

  useEffect(() => {
    if (!containerRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = null; // Transparent background for CSS grid
    sceneRef.current = scene;

    // Camera setup
    const camera = new THREE.PerspectiveCamera(
      75,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.set(5, 5, 5);
    cameraRef.current = camera;

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ 
      antialias: true, 
      alpha: true, // Make canvas transparent
      preserveDrawingBuffer: true // For screenshots
    });
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    rendererRef.current = renderer;

    // Controls setup
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.autoRotate = autoRotate;
    controls.autoRotateSpeed = 2.0;
    controlsRef.current = controls;

    // Lighting setup - stationary lights for consistent shiny appearance
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambientLight);

    // Main directional light (key light) - stationary position
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 10, 5);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    directionalLight.shadow.camera.near = 0.1;
    directionalLight.shadow.camera.far = 50;
    directionalLight.shadow.camera.left = -10;
    directionalLight.shadow.camera.right = 10;
    directionalLight.shadow.camera.top = 10;
    directionalLight.shadow.camera.bottom = -10;
    scene.add(directionalLight);

    // Fill light from opposite side - stationary
    const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
    fillLight.position.set(-8, 5, -8);
    scene.add(fillLight);

    // Rim light for better definition - stationary
    const rimLight = new THREE.DirectionalLight(0xffffff, 0.2);
    rimLight.position.set(0, -5, 10);
    scene.add(rimLight);

    // Load model
    loadModel(modelUrl, scene);

    // Add to DOM
    containerRef.current.appendChild(renderer.domElement);

    // Animation loop
    const animate = () => {
      animationIdRef.current = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    // Handle resize
    const handleResize = () => {
      if (!containerRef.current || !camera || !renderer) return;
      
      camera.aspect = containerRef.current.clientWidth / containerRef.current.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (animationIdRef.current) {
        cancelAnimationFrame(animationIdRef.current);
      }
      if (containerRef.current && renderer.domElement) {
        containerRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  // Update auto-rotate
  useEffect(() => {
    if (controlsRef.current) {
      controlsRef.current.autoRotate = autoRotate;
    }
  }, [autoRotate]);

  // Update model visibility
  useEffect(() => {
    if (modelRef.current) {
      modelRef.current.visible = isVisible;
    }
  }, [isVisible]);

  // Update wireframe visibility
  useEffect(() => {
    console.log(`🔍 Wireframe toggle triggered. showWireframe: ${showWireframe}`);
    
    const updateWireframeVisibility = () => {
      // Try direct reference first
      if (wireframeMeshRef.current) {
        wireframeMeshRef.current.visible = showWireframe;
        console.log(`🔍 Wireframe visibility set via direct ref: ${showWireframe}`);
        return true;
      }
      
      // Fallback: search in model group
      if (modelRef.current && modelRef.current.isGroup) {
        const wireframeMesh = modelRef.current.children.find(child => 
          child.name === 'LoadedModelWireframe'
        );
        if (wireframeMesh) {
          wireframeMesh.visible = showWireframe;
          wireframeMeshRef.current = wireframeMesh; // Update reference
          console.log(`🔍 Found and updated wireframe in group: ${showWireframe}`);
          return true;
        }
      }
      
      // Last resort: search entire scene and handle multiple wireframes (OBJ)
      if (sceneRef.current) {
        let found = false;
        sceneRef.current.traverse((child) => {
          if (child.name === 'LoadedModelWireframe') {
            child.visible = showWireframe;
            wireframeMeshRef.current = child; // Update reference
            console.log(`🔍 Found wireframe in scene traverse: ${showWireframe}`);
            found = true;
          }
        });
        
        // Handle OBJ files with multiple wireframes
        if (modelRef.current && modelRef.current.userData && modelRef.current.userData.wireframeMeshes) {
          const wireframes = modelRef.current.userData.wireframeMeshes;
          wireframes.forEach(wireframe => {
            wireframe.visible = showWireframe;
          });
          console.log(`🔍 Updated ${wireframes.length} OBJ wireframes: ${showWireframe}`);
          found = true;
        }
        
        if (found) return true;
      }
      
      console.log('🔍 No wireframe mesh found anywhere');
      return false;
    };
    
    // Try to update wireframe visibility immediately
    const success = updateWireframeVisibility();
    
    // If immediate update failed, retry with multiple attempts
    if (!success) {
      console.log('🔍 Immediate wireframe update failed, retrying...');
      const retryAttempts = [50, 100, 200, 500];
      
      retryAttempts.forEach((delay, index) => {
        setTimeout(() => {
          const retrySuccess = updateWireframeVisibility();
          if (retrySuccess) {
            console.log(`🔍 Wireframe update succeeded on retry ${index + 1} (${delay}ms)`);
          } else if (index === retryAttempts.length - 1) {
            console.log('🔍 All wireframe update retries failed');
            // Force a render to ensure any changes are visible
            if (sceneRef.current && renderer) {
              renderer.render(sceneRef.current, camera);
            }
          }
        }, delay);
      });
    }
  }, [showWireframe]);

  // Update material
  useEffect(() => {
    if (!modelRef.current || !material) return;

    console.log('🔍 Updating material:', material);
    
    const applyProps = (mat) => {
      if (mat instanceof THREE.MeshStandardMaterial) {
        // Only apply valid Three.js properties
        if (material.color) mat.color.setStyle(material.color);
        if (typeof material.metalness === 'number') mat.metalness = material.metalness;
        if (typeof material.roughness === 'number') mat.roughness = material.roughness;
        mat.needsUpdate = true;
        console.log('🔍 Applied material props to:', mat);
      }
    };

    // Handle grouped meshes (our case with solid + wireframe)
    if (modelRef.current.isGroup) {
      modelRef.current.children.forEach((child) => {
        if (child.isMesh && child.name === 'LoadedModel') {
          // Only apply to the solid mesh, not wireframe
          if (Array.isArray(child.material)) {
            child.material.forEach(applyProps);
          } else {
            applyProps(child.material);
          }
        }
      });
    } else {
      // Handle single mesh
      const mesh = modelRef.current;
      if (Array.isArray(mesh.material)) {
        mesh.material.forEach(applyProps);
      } else {
        applyProps(mesh.material);
      }
    }

    if (material.textureUrl) {
      const loader = new THREE.TextureLoader();
      loader.load(
        material.textureUrl,
        (tex) => {
          tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
          tex.anisotropy = 8;
          
          const applyTexture = (mat) => {
            if (mat instanceof THREE.MeshStandardMaterial) {
              mat.map = tex;
              mat.needsUpdate = true;
            }
          };

          // Handle grouped meshes
          if (modelRef.current.isGroup) {
            modelRef.current.children.forEach((child) => {
              if (child.isMesh && child.name === 'LoadedModel') {
                if (Array.isArray(child.material)) {
                  child.material.forEach(applyTexture);
                } else {
                  applyTexture(child.material);
                }
              }
            });
          } else {
            // Handle single mesh
            const mesh = modelRef.current;
            if (Array.isArray(mesh.material)) {
              mesh.material.forEach(applyTexture);
            } else {
              applyTexture(mesh.material);
            }
          }
        },
        undefined,
        () => {}
      );
    } else {
      // Clear texture if none selected
      const clearTexture = (mat) => {
        if (mat instanceof THREE.MeshStandardMaterial) {
          mat.map = null;
          mat.needsUpdate = true;
        }
      };

      // Handle grouped meshes
      if (modelRef.current.isGroup) {
        modelRef.current.children.forEach((child) => {
          if (child.isMesh && child.name === 'LoadedModel') {
            if (Array.isArray(child.material)) {
              child.material.forEach(clearTexture);
            } else {
              clearTexture(child.material);
            }
          }
        });
      } else {
        // Handle single mesh
        const mesh = modelRef.current;
        if (Array.isArray(mesh.material)) {
          mesh.material.forEach(clearTexture);
        } else {
          clearTexture(mesh.material);
        }
      }
    }
  }, [material]);

  // Load new model when URL changes
  useEffect(() => {
    if (sceneRef.current) {
      loadModel(modelUrl, sceneRef.current);
    }
  }, [modelUrl]);

  // Show info about OpenCascade.js status on component mount
  useEffect(() => {
    console.log('🔧 ThreeViewer initialized - OpenCascade.js enabled for native STEP/IGES support');
  }, []);

  // Handle fullscreen changes
  useEffect(() => {
    console.log(`🔍 Fullscreen state changed to: ${isFullscreen}`);
    
    // Multiple resize attempts to ensure proper sizing
    const resizeAttempts = [50, 100, 200, 500];
    
    resizeAttempts.forEach(delay => {
      setTimeout(() => {
        if (containerRef.current && cameraRef.current && rendererRef.current) {
          const camera = cameraRef.current;
          const renderer = rendererRef.current;
          const container = containerRef.current;
          
          const width = container.clientWidth;
          const height = container.clientHeight;
          
          console.log(`🔍 Resize attempt (${delay}ms): ${width}x${height}`);
          
          camera.aspect = width / height;
          camera.updateProjectionMatrix();
          renderer.setSize(width, height);
          
          // Force a render
          if (sceneRef.current) {
            renderer.render(sceneRef.current, camera);
          }
        }
      }, delay);
    });
  }, [isFullscreen]);

  // ✅ Load and initialize OpenCascade.js (browser-compatible)
  const loadOpenCascade = async () => {
    // If already loaded, return cached instance
    if (window.oc) {
      console.log("🧠 OpenCascade.js already loaded, reusing existing instance");
      return window.oc;
    }

    try {
      console.log("🔄 Initializing OpenCascade.js...");

      // Dynamic import to ensure compatibility with Vite and ESM bundling
      const ocModule = await import("opencascade.js");

      // Determine the init function
      const ocInit =
        ocModule.default ||
        ocModule.initOpenCascade ||
        (typeof ocModule === "function" ? ocModule : null);

      if (!ocInit) {
        throw new Error("OpenCascade init function not found — invalid module structure");
      }

      // ✅ Proper initialization (passing configuration object, not string)
      const oc = await ocInit({
        locateFile: (path) => {
          console.log(`📦 OpenCascade requesting: ${path}`);
          if (path.endsWith(".wasm")) {
            // Ensure your public folder has: public/opencascade.wasm
            return `/opencascade.wasm`;
          }
          return path;
        },
      });

      // Cache globally
      window.oc = oc;
      console.log("✅ OpenCascade.js initialized successfully");
      return oc;

    } catch (error) {
      console.error("❌ Error loading OpenCascade:", error);
      console.warn("⚠️ Falling back to alternative formats (STL, OBJ, etc.)");
      throw error;
    }
  };

  const loadModel = (url, scene) => {
    // Remove existing model and clear references
    if (modelRef.current) {
      scene.remove(modelRef.current);
    }
    
    // Clear wireframe reference and reset state
    wireframeMeshRef.current = null;
    console.log('🔍 Cleared wireframe reference and model state');
    
    // Force clear any lingering wireframe meshes in the scene
    const wireframesToRemove = [];
    scene.traverse((child) => {
      if (child.name === 'LoadedModelWireframe') {
        wireframesToRemove.push(child);
      }
    });
    wireframesToRemove.forEach(wireframe => {
      if (wireframe.parent) {
        wireframe.parent.remove(wireframe);
      }
    });
    if (wireframesToRemove.length > 0) {
      console.log(`🔍 Removed ${wireframesToRemove.length} lingering wireframe meshes`);
    }

    // Extract file extension from URL, handling S3 pre-signed URLs with query parameters
    const urlWithoutParams = url.split('?')[0]; // Remove query parameters
    const fileExtension = urlWithoutParams.split('.').pop()?.toLowerCase();
    
    console.log(`🔍 3D Loader - Original URL: ${url.substring(0, 100)}...`);
    console.log(`🔍 3D Loader - Clean URL: ${urlWithoutParams}`);
    console.log(`🔍 3D Loader - Detected extension: ${fileExtension}`);
    
    if (fileExtension === 'stl') {
      const loader = new STLLoader();
      
      // Add progress handler for large files
      const onProgress = (xhr) => {
        if (xhr.lengthComputable) {
          const percentComplete = (xhr.loaded / xhr.total) * 100;
          if (percentComplete < 100) {
            toast.info(`Loading model: ${Math.round(percentComplete)}%`);
          }
        }
      };

      loader.load(
        url,
        (geometry) => {
          try {
            console.log('🔍 STL Geometry loaded:', geometry);
            
            // Validate geometry
            if (!geometry.attributes.position || geometry.attributes.position.count === 0) {
              throw new Error('Invalid STL geometry');
            }

            console.log(`🔍 Vertex count: ${geometry.attributes.position.count}`);
            
            // STL files can contain multiple disconnected meshes
            // Compute normals for better rendering (mergeVertices not available in this Three.js version)
            geometry.computeVertexNormals();
            console.log('🔍 STL geometry normals computed');

            // Use theme-aware default material color with shiny surface
            const materialProps = material || { 
              color: document.documentElement.classList.contains('dark') ? '#60a5fa' : '#2563eb', 
              metalness: 0.7, // More metallic for shiny look
              roughness: 0.1  // Less rough for shiny surface
            };

            // Extract only valid Three.js material properties
            const validMaterialProps = {
              color: materialProps.color,
              metalness: materialProps.metalness,
              roughness: materialProps.roughness,
              wireframe: false,
              transparent: false,
              opacity: 1.0,
              envMapIntensity: 1.0 // Enhance reflections
            };

            const meshMaterial = new THREE.MeshStandardMaterial(validMaterialProps);
            
            // Add wireframe overlay for better visibility
            const wireframeMaterial = new THREE.MeshBasicMaterial({
              color: 0x00ff00, // Bright green wireframe
              wireframe: true,
              transparent: true,
              opacity: 1.0, // Fully opaque
              depthTest: false, // Render on top
              depthWrite: false // Don't write to depth buffer
            });

            // Create meshes first without any transformations
            const mesh = new THREE.Mesh(geometry, meshMaterial);
            mesh.castShadow = true;
            mesh.receiveShadow = true;
            mesh.name = 'LoadedModel';
            
            // Create wireframe with the same geometry
            const wireframeMesh = new THREE.Mesh(geometry.clone(), wireframeMaterial);
            wireframeMesh.name = 'LoadedModelWireframe';
            wireframeMesh.visible = showWireframe;
            wireframeMesh.renderOrder = 1;
            
            // Create group and add both meshes
            const group = new THREE.Group();
            group.add(mesh);
            group.add(wireframeMesh);
            group.name = 'LoadedModelGroup';
            
            // Calculate bounding box AFTER creating the group
            geometry.computeBoundingBox();
            const box = geometry.boundingBox;
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());
            
            console.log('🔍 Model bounding box:', {
              min: box.min,
              max: box.max,
              center: center,
              size: size
            });
            
            // Position the group to center it and place it on the grid
            group.position.set(-center.x, -box.min.y, -center.z);

            // Scale model if it's too small or too large
            const maxDimension = Math.max(size.x, size.y, size.z);
            console.log('🔍 Max dimension:', maxDimension);
            
            // Apply scaling to both meshes
            if (maxDimension < 0.1) {
              // Model is too small, scale it up
              const scaleFactor = 2 / maxDimension;
              group.scale.setScalar(scaleFactor);
              console.log('🔍 Scaling up small model by factor:', scaleFactor);
            } else if (maxDimension > 100) {
              // Model is too large, scale it down
              const scaleFactor = 10 / maxDimension;
              group.scale.setScalar(scaleFactor);
              console.log('🔍 Scaling down large model by factor:', scaleFactor);
            }
            
            // Store wireframe reference for toggle
            wireframeMeshRef.current = wireframeMesh;
            console.log('🔍 Wireframe mesh reference stored:', wireframeMesh);
            
            modelRef.current = group;
            scene.add(group);
            
            // Ensure wireframe visibility is set correctly after loading
            setTimeout(() => {
              if (wireframeMeshRef.current) {
                wireframeMeshRef.current.visible = showWireframe;
                console.log(`🔍 Wireframe visibility set to: ${showWireframe} after STL load`);
                
                // Force a render to ensure visibility change is applied
                if (sceneRef.current && renderer) {
                  renderer.render(sceneRef.current, camera);
                }
              }
            }, 100);
            
            console.log('🔍 Model added to scene with wireframe overlay, calling fitToView...');
            
            // Fit to view
            fitToView();
            
            console.log('✅ STL model loaded and positioned successfully');
          } catch (error) {
            console.error('Error creating mesh:', error);
            toast.error('Failed to create 3D model - Using fallback cube');
            // Create fallback cube on error
            const geometry = new THREE.BoxGeometry(1, 1, 1);
            const materialProps = material || { 
              color: '#ef4444', // Red color for error state
              metalness: 0.1,
              roughness: 0.3 
            };
            const meshMaterial = new THREE.MeshStandardMaterial(materialProps);
            const mesh = new THREE.Mesh(geometry, meshMaterial);
            mesh.castShadow = true;
            mesh.receiveShadow = true;
            mesh.name = 'ErrorFallbackModel';
            modelRef.current = mesh;
            scene.add(mesh);
            fitToView();
          }
        },
        undefined,
        onProgress,
        (error) => {
          console.error('Error loading STL:', error);
          toast.error('Failed to load 3D model: ' + (error.message || 'Unknown error'));
          
          // Load fallback cube on error
          const geometry = new THREE.BoxGeometry(1, 1, 1);
          const materialProps = {
            color: '#ef4444', // Red color for error state 
            metalness: 0.1,
            roughness: 0.3
          };
          const meshMaterial = new THREE.MeshStandardMaterial(materialProps);
          const mesh = new THREE.Mesh(geometry, meshMaterial);
          mesh.castShadow = true;
          mesh.receiveShadow = true;
          mesh.name = 'ErrorFallbackModel';
          modelRef.current = mesh;
          scene.add(mesh);
          fitToView();
        }
      );
    } else if (fileExtension === 'gltf' || fileExtension === 'glb') {
      const loader = new GLTFLoader();
      loader.load(
        url,
        (gltf) => {
          const model = gltf.scene;
          model.name = 'LoadedModel';
          
          // Center the model above the grid
          const box = new THREE.Box3().setFromObject(model);
          const center = box.getCenter(new THREE.Vector3());
          
          // Position model so it sits on the grid
          model.position.set(-center.x, -box.min.y, -center.z);
          
          modelRef.current = model;
          scene.add(model);
          fitToView();
        },
        undefined,
        (error) => {
          console.error('Error loading GLTF:', error);
          toast.error('Failed to load 3D model');
        }
      );
    } else if (fileExtension === 'obj') {
      const loader = new OBJLoader();
      loader.load(
        url,
        (object) => {
          console.log('🔍 OBJ Object loaded:', object);
          
          // Count meshes in the object
          let meshCount = 0;
          object.traverse((child) => {
            if (child.isMesh) meshCount++;
          });
          console.log(`🔍 OBJ contains ${meshCount} separate meshes`);
          
          // Apply material to all meshes in the object
          const materialProps = material || { 
            color: document.documentElement.classList.contains('dark') ? '#60a5fa' : '#2563eb', 
            metalness: 0.7, // More metallic for shiny look
            roughness: 0.1  // Less rough for shiny surface
          };
          
          // Extract only valid Three.js material properties
          const validMaterialProps = {
            color: materialProps.color,
            metalness: materialProps.metalness,
            roughness: materialProps.roughness,
            envMapIntensity: 1.0
          };
          
          const meshMaterial = new THREE.MeshStandardMaterial(validMaterialProps);

          // Create wireframe material for OBJ
          const wireframeMaterial = new THREE.MeshBasicMaterial({
            color: 0x00ff00,
            wireframe: true,
            transparent: true,
            opacity: 1.0,
            depthTest: false,
            depthWrite: false
          });

          // Apply materials and create wireframe for each mesh
          const wireframeMeshes = [];
          object.traverse((child) => {
            if (child.isMesh) {
              // Apply solid material
              child.material = meshMaterial;
              child.castShadow = true;
              child.receiveShadow = true;
              
              // Create wireframe version
              const wireframeMesh = new THREE.Mesh(child.geometry, wireframeMaterial);
              wireframeMesh.position.copy(child.position);
              wireframeMesh.rotation.copy(child.rotation);
              wireframeMesh.scale.copy(child.scale);
              wireframeMesh.visible = showWireframe;
              wireframeMesh.renderOrder = 1;
              wireframeMeshes.push(wireframeMesh);
              
              // Add wireframe to the same parent
              if (child.parent) {
                child.parent.add(wireframeMesh);
              }
            }
          });

          // Store reference to first wireframe mesh for toggle
          if (wireframeMeshes.length > 0) {
            wireframeMeshRef.current = wireframeMeshes[0];
            // Store all wireframes for complete toggle
            object.userData.wireframeMeshes = wireframeMeshes;
            console.log(`🔍 Created ${wireframeMeshes.length} wireframe meshes for OBJ`);
            
            // Ensure wireframe visibility is set correctly after loading
            setTimeout(() => {
              wireframeMeshes.forEach(wireframe => {
                wireframe.visible = showWireframe;
              });
              console.log(`🔍 Wireframe visibility set to: ${showWireframe} after OBJ load`);
              
              // Force a render to ensure visibility change is applied
              if (sceneRef.current && renderer) {
                renderer.render(sceneRef.current, camera);
              }
            }, 100);
          }

          object.name = 'LoadedModel';
          
          // Center the model above the grid
          const box = new THREE.Box3().setFromObject(object);
          const center = box.getCenter(new THREE.Vector3());
          
          // Position model so it sits on the grid
          object.position.set(-center.x, -box.min.y, -center.z);
          
          modelRef.current = object;
          scene.add(object);
          fitToView();
        },
        undefined,
        (error) => {
          console.error('Error loading OBJ:', error);
          toast.error('Failed to load OBJ model');
          loadPlaceholderModel(scene, 'OBJ');
        }
      );
    } else if (fileExtension === 'step' || fileExtension === 'stp') {
      // STEP files - try OpenCascade.js first, then fallback to alternatives
      console.log('🔧 STEP file detected - trying OpenCascade.js with fallback');
      toast.info('Loading STEP file...');
      loadSTEPFile(url, scene);
    } else if (fileExtension === 'iges' || fileExtension === 'igs') {
      // IGES files - try OpenCascade.js first, then fallback to alternatives
      console.log('🔧 IGES file detected - trying OpenCascade.js with fallback');
      toast.info('Loading IGES file...');
      loadIGESFile(url, scene);
    } else if (fileExtension === 'fcstd') {
      // FreeCAD files maintain full assembly structure but need conversion for web preview  
      toast.success('FCSTD file detected! This format preserves full assembly structure. Showing placeholder for preview.');
      loadPlaceholderModel(scene, 'FCSTD (Assembled)');
    } else if (fileExtension === 'dxf') {
      // DXF is typically 2D, show placeholder
      toast.info('DXF preview uses a placeholder. Download works from the buttons below.');
      loadPlaceholderModel(scene, 'DXF');
    } else if (fileExtension === 'dwg') {
      // DWG is not directly supported by three.js
      toast.info('DWG preview uses a placeholder. Download works from the buttons below.');
      loadPlaceholderModel(scene, 'DWG');
    } else {
      toast.warning(`Unsupported file format: ${fileExtension}`);
      loadPlaceholderModel(scene, 'Unknown');
    }
  };

  // ✅ Function to load and parse STEP file using OpenCascade.js
  const loadSTEPFile = async (url, scene) => {
    try {
      console.log(`📂 Loading STEP file from: ${url}`);

      // Ensure OpenCascade is initialized
      const oc = await loadOpenCascade();
      if (!oc) throw new Error("OpenCascade not initialized");

      // Fetch the STEP file
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to fetch STEP file: ${response.status}`);
      }

      // Read file as ArrayBuffer
      const arrayBuffer = await response.arrayBuffer();
      const data = new Uint8Array(arrayBuffer);

      console.log("🔍 Parsing STEP file with OpenCascade...");

      // Create a new reader instance
      const reader = new oc.STEPControl_Reader_1();

      // Write file to OpenCascade virtual filesystem (safer approach)
      oc.FS.writeFile('/temp.step', data);
      
      // Load the file using filesystem path
      let status;
      if (typeof reader.ReadFile === "function") {
        // Most modern OpenCascade.js builds use this
        console.log("✅ Using ReadFile()");
        status = reader.ReadFile('/temp.step');
      } else if (typeof reader.ReadFile_1 === "function") {
        // Older versions or emscripten-overloaded bindings
        console.log("✅ Using ReadFile_1()");
        const dataString = new TextDecoder().decode(data);
        status = reader.ReadFile_1(dataString);
      } else {
        throw new Error("❌ STEPControl_Reader.ReadFile method not found in OpenCascade build");
      }

      if (status !== oc.IFSelect_ReturnStatus.IFSelect_RetDone) {
        throw new Error("Failed to read STEP file: Invalid or corrupted format");
      }

      // Transfer the roots to shapes
      const numRoots = reader.NbRootsForTransfer();
      console.log(`📊 Number of roots found: ${numRoots}`);

      reader.TransferRoots();
      const shape = reader.OneShape();

      if (!shape || shape.IsNull()) {
        throw new Error("No valid shape found in STEP file");
      }

      console.log("🧱 Converting shape to mesh...");

      // Create a shape tessellator
      const tess = new oc.BRepMesh_IncrementalMesh_2(
        shape,
        0.1, // precision
        false, // parallel
        0.1, // deflection angle
        true // relative
      );

      tess.Perform_1();

      // Robust shape → mesh conversion with enum auto-discovery
      try {
        console.log("🧱 Converting shape to mesh (robust)...");

        // --- 1) Find usable enum constants for TopAbs_FACE and a stop enum ---
        const enumCandidates = [
          "TopAbs_FACE",
          "TopAbs_ShapeEnum",   // some builds prefix differently
          "TopAbs_Shape",
          "TopAbs_Face",
        ];

        let FaceEnum = null;
        let StopEnum = null;

        for (const name of enumCandidates) {
          if (oc[name]) {
            // In some builds enum is object {0: '...', value: 2} or function; try to use it
            FaceEnum = oc[name];
            break;
          }
        }

        // If FaceEnum still null, try to look up any object containing 'FACE' or 'Face'
        if (!FaceEnum) {
          for (const k of Object.keys(oc)) {
            if (/FACE/i.test(k) && typeof oc[k] !== "undefined") {
              FaceEnum = oc[k];
              break;
            }
          }
        }

        // For the stop enum, prefer TopAbs_SHAPE or whatever exists
        const stopCandidates = ["TopAbs_SHAPE", "TopAbs_COMPOUND", "TopAbs_SOLID", "TopAbs_SHAPEEnum"];
        for (const name of stopCandidates) {
          if (oc[name]) {
            StopEnum = oc[name];
            break;
          }
        }

        // If still null choose FaceEnum (we'll pass same for both) — some constructors accept same
        if (!StopEnum && FaceEnum) StopEnum = FaceEnum;

        // If we couldn't find FaceEnum at all, abort to fallback
        if (!FaceEnum) {
          console.warn("⚠️ Could not discover TopAbs_FACE enum in this OpenCascade build, falling back.");
          throw new Error("Missing TopAbs_FACE enum");
        }

        // --- 2) Create TopExp_Explorer robustly trying different constructor options ---
        let exp;
        let expCtorTried = null;
        const tryCreateExplorer = () => {
          // Try 3-arg constructor: (shape, toFind, toStop)
          try {
            expCtorTried = "3-arg";
            return new oc.TopExp_Explorer(shape, FaceEnum, StopEnum);
          } catch (e) {
            // swallow and continue
          }
          // Try 2-arg constructor: (shape, toFind)
          try {
            expCtorTried = "2-arg";
            return new oc.TopExp_Explorer(shape, FaceEnum);
          } catch (e) {
            // swallow and continue
          }
          // Try using explicit export name variant (some builds expose TopExp_Explorer_2 / _3)
          const altNames = ["TopExp_Explorer_3", "TopExp_Explorer_2"];
          for (const name of altNames) {
            if (oc[name]) {
              try {
                expCtorTried = name;
                // if it's a factory/class function, attempt call
                return new oc[name](shape, FaceEnum, StopEnum);
              } catch (_) {}
            }
          }
          return null;
        };

        exp = tryCreateExplorer();
        if (!exp) {
          console.error("❌ Could not create TopExp_Explorer with any known signature.");
          throw new Error("Failed to create TopExp_Explorer: incompatible OpenCascade.js build");
        }

        console.log(`🔎 TopExp_Explorer created using: ${expCtorTried}`);

        // --- 3) Iterate faces and extract triangulation (safe checks added) ---
        const vertices = [];
        const indices = [];
        let globalVertexOffset = 0;

        // Helper to convert point object to coords (handles different bindings)
        const getPointCoords = (pnt) => {
          if (!pnt) return [0, 0, 0];
          // some builds use methods X,Y,Z; some properties x,y,z
          const x = (typeof pnt.X === "function") ? pnt.X() : (pnt.x ?? pnt.X ?? 0);
          const y = (typeof pnt.Y === "function") ? pnt.Y() : (pnt.y ?? pnt.Y ?? 0);
          const z = (typeof pnt.Z === "function") ? pnt.Z() : (pnt.z ?? pnt.Z ?? 0);
          return [x, y, z];
        };

        // Walk through faces
        for (; exp.More(); exp.Next()) {
          // Each Current() may be a TopoDS_Face or something; ensure we get face object
          const faceHandle = exp.Current();
          if (!faceHandle) continue;

          // Some builds wrap TopoDS_Face differently — attempt accessors
          let face;
          try {
            face = oc.TopoDS.prototype.Face ? oc.TopoDS.prototype.Face(faceHandle) : faceHandle;
          } catch (e) {
            // fallback: assume faceHandle is already a face
            face = faceHandle;
          }

          // Triangulation retrieval: BRep_Tool.Triangulation(face, loc)
          let triangulation = null;
          try {
            const location = new oc.TopLoc_Location_1(); // may be required in some bindings
            if (typeof oc.BRep_Tool.Triangulation === "function") {
              triangulation = oc.BRep_Tool.Triangulation(face, location);
            } else if (typeof oc.BRep_Tool.prototype.Triangulation === "function") {
              triangulation = oc.BRep_Tool.prototype.Triangulation(face, location);
            } else {
              // Try variant with only one param
              triangulation = oc.BRep_Tool.Triangulation(face);
            }
          } catch (e) {
            console.warn("⚠️ Triangulation retrieval failed for a face; skipping this face.", e);
            continue;
          }

          if (!triangulation || triangulation.IsNull && triangulation.IsNull()) {
            // no triangulation available for this face
            continue;
          }

          // Get nodes and triangles — bindings may expose different methods
          let nodes, triangles;
          try {
            nodes = triangulation.Nodes ? triangulation.Nodes() : triangulation.getNodes ? triangulation.getNodes() : null;
            triangles = triangulation.Triangles ? triangulation.Triangles() : triangulation.getTriangles ? triangulation.getTriangles() : null;
          } catch (e) {
            console.warn("⚠️ Failed to access Nodes/Triangles for triangulation, skipping face.", e);
            continue;
          }

          if (!nodes || !triangles) continue;

          // nodes is 1-based in OCC; try to handle Length() or size
          const nodeLen = (typeof nodes.Length === "function") ? nodes.Length() : (nodes.size ? nodes.size() : 0);
          for (let i = 1; i <= nodeLen; i++) {
            const pnt = nodes.Value ? nodes.Value(i) : nodes.get ? nodes.get(i) : null;
            const [x, y, z] = getPointCoords(pnt);
            vertices.push(x, y, z);
          }

          const triLen = (typeof triangles.Length === "function") ? triangles.Length() : (triangles.size ? triangles.size() : 0);
          for (let i = 1; i <= triLen; i++) {
            const tri = triangles.Value ? triangles.Value(i) : triangles.get ? triangles.get(i) : null;
            if (!tri) continue;
            const n1 = tri.Value ? tri.Value(1) : (tri.get ? tri.get(0) : null);
            const n2 = tri.Value ? tri.Value(2) : (tri.get ? tri.get(1) : null);
            const n3 = tri.Value ? tri.Value(3) : (tri.get ? tri.get(2) : null);

            if (n1 == null || n2 == null || n3 == null) continue;
            // convert 1-based indices to 0-based and offset by globalVertexOffset
            indices.push(globalVertexOffset + (n1 - 1));
            indices.push(globalVertexOffset + (n2 - 1));
            indices.push(globalVertexOffset + (n3 - 1));
          }

          // increment the offset by number of nodes we just appended
          globalVertexOffset += nodeLen;
        }

        // If no triangles/vertices collected -> fallback
        if (vertices.length === 0 || indices.length === 0) {
          console.warn("⚠️ No triangulation produced from STEP shape — falling back.");
          throw new Error("No triangulation produced");
        }

        // --- 4) Build Three.js geometry and add to scene ---
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute("position", new THREE.Float32BufferAttribute(vertices, 3));
        geometry.setIndex(indices);
        geometry.computeVertexNormals();

        const material = new THREE.MeshStandardMaterial({ 
          color: 0xcccccc, 
          metalness: 0.2, 
          roughness: 0.8 
        });
        
        const mesh = new THREE.Mesh(geometry, material);
        mesh.name = 'LoadedModel';
        mesh.castShadow = true;
        mesh.receiveShadow = true;

        // Create wireframe overlay for STEP files
        const wireframeMaterial = new THREE.MeshBasicMaterial({
          color: 0x00ff00, // Bright green wireframe
          wireframe: true,
          transparent: true,
          opacity: 1.0,
          depthTest: false,
          renderOrder: 1
        });

        const wireframeMesh = new THREE.Mesh(geometry.clone(), wireframeMaterial);
        wireframeMesh.name = 'LoadedModelWireframe';
        wireframeMesh.visible = showWireframe;
        wireframeMesh.renderOrder = 1;

        // Create group and add both meshes
        const group = new THREE.Group();
        group.add(mesh);
        group.add(wireframeMesh);
        group.name = 'LoadedModelGroup';

        scene.add(group);
        modelRef.current = group;

        // Store wireframe reference for toggle
        wireframeMeshRef.current = wireframeMesh;
        console.log('🔍 STEP wireframe mesh reference stored:', wireframeMesh);
        
        // Ensure wireframe visibility is set correctly after loading
        setTimeout(() => {
          if (wireframeMeshRef.current) {
            wireframeMeshRef.current.visible = showWireframe;
            console.log(`🔍 Wireframe visibility set to: ${showWireframe} after STEP load`);
            
            // Force a render to ensure visibility change is applied
            if (sceneRef.current && renderer) {
              renderer.render(sceneRef.current, camera);
            }
          }
        }, 100);

        console.log("✅ STEP file converted and mesh added to scene (robust path).");

      } catch (conversionError) {
        console.error("❌ Shape conversion failed:", conversionError);
        throw conversionError; // Will be caught by outer try-catch and trigger fallback
      }

      // Fit to view
      fitToView();

      // Cleanup temporary file
      try {
        oc.FS.unlink('/temp.step');
      } catch (cleanupError) {
        console.warn('⚠️ Could not cleanup temp file:', cleanupError);
      }

      console.log("✅ STEP file loaded successfully!");
      toast.success('STEP file loaded successfully!');

    } catch (error) {
      console.error("❌ Error loading STEP file:", error);
      
      // Cleanup temporary file on error
      try {
        if (window.oc && window.oc.FS) {
          window.oc.FS.unlink('/temp.step');
        }
      } catch (cleanupError) {
        // Ignore cleanup errors
      }
      
      // If OpenCascade.js failed to load, try alternative formats
      if (error.message.includes('OpenCascade') || 
          error.message.includes('not initialized') || 
          error.message.includes('ReadFile') ||
          error.message.includes('No triangulation produced') ||
          error.message.includes('Missing TopAbs_FACE enum') ||
          error.message.includes('Failed to create TopExp_Explorer')) {
        console.log('🔄 OpenCascade unavailable, trying alternative formats for STEP file');
        toast.info('Loading alternative format for STEP file...');
        loadSTEPAlternative(url, scene);
      } else {
        toast.error(`Failed to load STEP file: ${error.message}`);
        // Show placeholder with download option
        toast.info('STEP file preview failed. You can still download the file using the buttons below.');
        loadPlaceholderModel(scene, 'STEP (Download Available)');
      }
    }
  };

  // Load IGES files using OpenCascade.js browser WASM build
  const loadIGESFile = async (url, scene) => {
    try {
      console.log(`📂 Loading IGES file from: ${url}`);
      const oc = await loadOpenCascade();
      if (!oc) throw new Error("OpenCascade not initialized");
      
      // Fetch the IGES file
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to fetch IGES file: ${response.status}`);
      }
      
      const arrayBuffer = await response.arrayBuffer();
      const data = new Uint8Array(arrayBuffer);

      console.log("🔍 Parsing IGES file with OpenCascade...");

      // Write file to OpenCascade virtual filesystem
      oc.FS.writeFile('/temp.iges', data);
      
      // Create a new reader instance
      const reader = new oc.IGESControl_Reader_1();
      
      // Load the file using filesystem path (same fix as STEP)
      let status;
      if (typeof reader.ReadFile === "function") {
        console.log("✅ Using ReadFile() for IGES");
        status = reader.ReadFile('/temp.iges');
      } else if (typeof reader.ReadFile_1 === "function") {
        console.log("✅ Using ReadFile_1() for IGES");
        const dataString = new TextDecoder().decode(data);
        status = reader.ReadFile_1(dataString);
      } else {
        throw new Error("❌ IGESControl_Reader.ReadFile method not found in OpenCascade build");
      }

      if (status !== oc.IFSelect_ReturnStatus.IFSelect_RetDone) {
        throw new Error("Failed to read IGES file: Invalid or corrupted format");
      }

      // Transfer the roots to shapes
      const numRoots = reader.NbRootsForTransfer();
      console.log(`📊 Number of roots found: ${numRoots}`);

      reader.TransferRoots();
      const shape = reader.OneShape();

      if (!shape || shape.IsNull()) {
        throw new Error("No valid shape found in IGES file");
      }

      console.log("🧱 Converting shape to mesh...");

      // Create a shape tessellator
      const tess = new oc.BRepMesh_IncrementalMesh_2(
        shape,
        0.1, // precision
        false, // parallel
        0.1, // deflection angle
        true // relative
      );

      tess.Perform_1();

      // Convert shape to triangulated geometry (same as STEP)
      const vertices = [];
      const faces = [];

      // Create TopExp_Explorer with version-agnostic approach
      let exp;
      try {
        // Newer API (3-arg constructor)
        exp = new oc.TopExp_Explorer_2(shape, oc.TopAbs_FACE, oc.TopAbs_SHAPE);
        console.log("✅ Using 3-arg TopExp_Explorer() for IGES");
      } catch (err) {
        console.warn("⚠️ TopExp_Explorer 3-arg constructor failed, trying 2-arg fallback:", err);
        try {
          // Fallback for older builds
          exp = new oc.TopExp_Explorer_2(shape, oc.TopAbs_FACE);
          console.log("✅ Using 2-arg TopExp_Explorer() for IGES");
        } catch (err2) {
          throw new Error("❌ Failed to create TopExp_Explorer: incompatible OpenCascade.js build");
        }
      }

      for (; exp.More(); exp.Next()) {
        const face = oc.TopoDS.prototype.Face(exp.Current());
        const location = new oc.TopLoc_Location_1();
        const triangulation = oc.BRep_Tool.prototype.Triangulation(face, location);

        if (!triangulation.IsNull()) {
          const nodes = triangulation.Nodes();
          const triangles = triangulation.Triangles();

          for (let i = 1; i <= nodes.Length(); i++) {
            const pnt = nodes.Value(i);
            vertices.push(pnt.X(), pnt.Y(), pnt.Z());
          }

          for (let i = 1; i <= triangles.Length(); i++) {
            const tri = triangles.Value(i);
            const n1 = tri.Value(1);
            const n2 = tri.Value(2);
            const n3 = tri.Value(3);
            faces.push(n1 - 1, n2 - 1, n3 - 1);
          }
        }
      }

      // Create Three.js geometry
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute("position", new THREE.Float32BufferAttribute(vertices, 3));
      geometry.setIndex(faces);
      geometry.computeVertexNormals();

      const material = new THREE.MeshStandardMaterial({
        color: 0xcccccc,
        metalness: 0.3,
        roughness: 0.7,
      });

      const mesh = new THREE.Mesh(geometry, material);
      scene.add(mesh);
      modelRef.current = mesh;

      // Fit to view
      fitToView();

      // Cleanup temporary file
      try {
        oc.FS.unlink('/temp.iges');
      } catch (cleanupError) {
        console.warn('⚠️ Could not cleanup temp file:', cleanupError);
      }

      console.log("✅ IGES file loaded successfully!");
      toast.success('IGES file loaded successfully!');
      
    } catch (error) {
      console.error("❌ Error loading IGES file:", error);
      
      // Cleanup temporary file on error
      try {
        if (window.oc && window.oc.FS) {
          window.oc.FS.unlink('/temp.iges');
        }
      } catch (cleanupError) {
        // Ignore cleanup errors
      }
      
      // If OpenCascade.js failed to load, try alternative formats
      if (error.message.includes('OpenCascade') || error.message.includes('not initialized') || error.message.includes('ReadFile')) {
        console.log('🔄 OpenCascade unavailable, trying alternative formats for IGES file');
        toast.info('Loading alternative format for IGES file...');
        loadIGESAlternative(url, scene);
      } else {
        toast.error(`Failed to load IGES file: ${error.message}`);
        // Show placeholder with download option
        toast.info('IGES file preview failed. You can still download the file using the buttons below.');
        loadPlaceholderModel(scene, 'IGES (Download Available)');
      }
    }
  };

  // Convert OpenCascade document to Three.js meshes
  const convertOCCToThreeJS = (oc, doc) => {
    const meshes = [];
    // This is a simplified conversion - in practice, you'd need more complex logic
    // to properly extract and convert all shapes from the document
    try {
      // Implementation would go here - this is a placeholder
      console.log('Converting OCC document to Three.js meshes...');
      return meshes;
    } catch (error) {
      console.error('Error converting OCC document:', error);
      return [];
    }
  };

  // Convert OpenCascade shape to Three.js meshes
  const convertShapeToThreeJS = async (oc, shape) => {
    const meshes = [];
    
    try {
      console.log('🔄 Converting OCC shape to Three.js meshes...');
      
      // Tessellate the shape to get triangular mesh
      const tessellator = new oc.BRepMesh_IncrementalMesh_2(shape, 0.1, false, 0.5, true);
      
      if (!tessellator.IsDone()) {
        throw new Error('Tessellation failed');
      }
      
      console.log('✅ Tessellation completed');
      
      // Explore the shape to find faces
      const explorer = new oc.TopExp_Explorer_2(shape, oc.TopAbs_ShapeEnum.TopAbs_FACE, oc.TopAbs_ShapeEnum.TopAbs_SHAPE);
      let faceCount = 0;
      
      while (explorer.More()) {
        const face = oc.TopoDS.Face_1(explorer.Current());
        
        try {
          // Get triangulation from face
          const location = new oc.TopLoc_Location_1();
          const triangulation = oc.BRep_Tool.Triangulation(face, location);
          
          if (!triangulation.IsNull()) {
            const vertices = [];
            const indices = [];
            const normals = [];
            
            // Extract vertices
            const nodeCount = triangulation.NbNodes();
            console.log(`📐 Face ${faceCount}: ${nodeCount} vertices`);
            
            for (let i = 1; i <= nodeCount; i++) {
              const node = triangulation.Node(i);
              vertices.push(node.X(), node.Y(), node.Z());
            }
            
            // Extract triangles
            const triangleCount = triangulation.NbTriangles();
            console.log(`🔺 Face ${faceCount}: ${triangleCount} triangles`);
            
            for (let i = 1; i <= triangleCount; i++) {
              const triangle = triangulation.Triangle(i);
              const n1 = triangle.Value(1) - 1; // Convert to 0-based indexing
              const n2 = triangle.Value(2) - 1;
              const n3 = triangle.Value(3) - 1;
              
              indices.push(n1, n2, n3);
            }
            
            // Create Three.js geometry
            if (vertices.length > 0 && indices.length > 0) {
              const geometry = new THREE.BufferGeometry();
              geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
              geometry.setIndex(indices);
              geometry.computeVertexNormals();
              
              // Create material
              const material = new THREE.MeshStandardMaterial({
                color: faceCount % 2 === 0 ? '#3b82f6' : '#10b981', // Alternate colors
                metalness: 0.7,
                roughness: 0.1,
                side: THREE.DoubleSide
              });
              
              const mesh = new THREE.Mesh(geometry, material);
              mesh.name = `STEPFace_${faceCount}`;
              mesh.castShadow = true;
              mesh.receiveShadow = true;
              
              meshes.push(mesh);
              faceCount++;
            }
          }
        } catch (faceError) {
          console.warn(`⚠️ Failed to process face ${faceCount}:`, faceError);
        }
        
        explorer.Next();
      }
      
      console.log(`✅ Converted ${faceCount} faces to Three.js meshes`);
      return meshes;
      
    } catch (error) {
      console.error('❌ Error converting OCC shape:', error);
      return [];
    }
  };

  // FALLBACK: Load STEP files by trying alternative formats from the same project
  // Used when OpenCascade.js fails to load
  const loadSTEPAlternative = async (stepUrl, scene) => {
    try {
      if (!projectId) {
        console.warn('⚠️ No project ID available, cannot try alternative formats');
        toast.info('STEP file failed to load. You can still download the file using the buttons below.');
        loadPlaceholderModel(scene, 'STEP (Download Available)');
        return;
      }

      console.log('🔄 Loading alternative formats for STEP file');
      toast.info('Trying alternative formats...');

      // Try formats in order: STL -> OBJ -> Placeholder
      const alternativeFormats = ['STL', 'OBJ'];
      let foundAlternative = false;
      
      for (const format of alternativeFormats) {
        try {
          console.log(`🔍 Checking for ${format} alternative...`);
          
          // Request proper download URL from backend API
          const response = await fetch(`/api/projects/${projectId}/download/${format}`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('cadscribe_token')}`
            }
          });
          
          if (response.ok) {
            const data = await response.json();
            const alternativeUrl = data.download_url;
            
            console.log(`✅ Found ${format} alternative, loading...`);
            toast.success(`Loading ${format} version...`);
            foundAlternative = true;
            
            // Load the alternative format
            if (format === 'STL') {
              loadSTLFromUrl(alternativeUrl, scene, 'STEP');
            } else if (format === 'OBJ') {
              loadOBJFromUrl(alternativeUrl, scene, 'STEP');
            }
            return;
          } else {
            console.log(`⚠️ ${format} not available - Status: ${response.status}`);
            const errorText = await response.text();
            console.log(`   Error: ${errorText}`);
          }
        } catch (formatError) {
          console.log(`⚠️ ${format} request failed:`, formatError.message);
        }
      }
      
      // If no alternatives found, show enhanced placeholder
      if (!foundAlternative) {
        console.log('❌ No alternative formats found');
        throw new Error('No viewable alternatives found');
      }
      
    } catch (error) {
      console.log('❌ Failed to load STEP alternatives:', error.message);
      toast.info('STEP file detected! Download available below for full assembly structure.');
      loadPlaceholderModel(scene, 'STEP (Download Available)');
    }
  };

  // FALLBACK: Load IGES files by trying alternative formats from the same project  
  // Used when OpenCascade.js fails to load
  const loadIGESAlternative = async (igesUrl, scene) => {
    try {
      if (!projectId) {
        console.warn('⚠️ No project ID available, cannot try alternative formats');
        toast.info('IGES file failed to load. You can still download the file using the buttons below.');
        loadPlaceholderModel(scene, 'IGES (Download Available)');
        return;
      }

      console.log('🔄 Loading alternative formats for IGES file');
      toast.info('Trying alternative formats...');

      // Try formats in order: STL -> OBJ -> Placeholder
      const alternativeFormats = ['STL', 'OBJ'];
      let foundAlternative = false;
      
      for (const format of alternativeFormats) {
        try {
          console.log(`🔍 Checking for ${format} alternative...`);
          
          // Request proper download URL from backend API
          const response = await fetch(`/api/projects/${projectId}/download/${format}`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('cadscribe_token')}`
            }
          });
          
          if (response.ok) {
            const data = await response.json();
            const alternativeUrl = data.download_url;
            
            console.log(`✅ Found ${format} alternative, loading...`);
            toast.success(`Loading ${format} version...`);
            foundAlternative = true;
            
            // Load the alternative format
            if (format === 'STL') {
              loadSTLFromUrl(alternativeUrl, scene, 'IGES');
            } else if (format === 'OBJ') {
              loadOBJFromUrl(alternativeUrl, scene, 'IGES');
            }
            return;
          } else {
            console.log(`⚠️ ${format} not available - Status: ${response.status}`);
            const errorText = await response.text();
            console.log(`   Error: ${errorText}`);
          }
        } catch (formatError) {
          console.log(`⚠️ ${format} request failed:`, formatError.message);
        }
      }
      
      // If no alternatives found, show enhanced placeholder
      if (!foundAlternative) {
        console.log('❌ No alternative formats found');
        throw new Error('No viewable alternatives found');
      }
      
    } catch (error) {
      console.log('❌ Failed to load IGES alternatives:', error.message);
      toast.info('IGES file detected! Download available below for full assembly structure.');
      loadPlaceholderModel(scene, 'IGES (Download Available)');
    }
  };

  // Extract project information from S3 URL
  const extractProjectInfoFromUrl = (url) => {
    try {
      // Match pattern: .../output/project-id/v1/project-id.format
      const match = url.match(/\/output\/([^\/]+)\/v(\d+)\/([^\/\?]+)/);
      if (match) {
        return {
          projectId: match[1],
          version: match[2],
          filename: match[3]
        };
      }
      return null;
    } catch (error) {
      console.error('Error extracting project info:', error);
      return null;
    }
  };

  // Load STL from URL with source format tracking
  const loadSTLFromUrl = (url, scene, sourceFormat = 'STL') => {
    const loader = new STLLoader();
    loader.load(
      url,
      (geometry) => {
        console.log(`🔍 ${sourceFormat} -> STL Geometry loaded:`, geometry);
        console.log(`🔍 Vertex count: ${geometry.attributes.position.count}`);
        
        geometry.computeVertexNormals();
        console.log(`🔍 ${sourceFormat} -> STL geometry normals computed`);

        // Create material with source format indication
        const materialProps = material || { 
          color: sourceFormat === 'STEP' ? '#10b981' : sourceFormat === 'IGES' ? '#3b82f6' : '#2563eb',
          metalness: 0.7,
          roughness: 0.1
        };

        const validMaterialProps = {
          color: materialProps.color,
          metalness: materialProps.metalness,
          roughness: materialProps.roughness,
          wireframe: false,
          transparent: false,
          opacity: 1.0,
          envMapIntensity: 1.0
        };

        const meshMaterial = new THREE.MeshStandardMaterial(validMaterialProps);
        
        const wireframeMaterial = new THREE.MeshBasicMaterial({
          color: 0x00ff00,
          wireframe: true,
          transparent: true,
          opacity: 1.0,
          depthTest: false,
          depthWrite: false
        });

        const mesh = new THREE.Mesh(geometry, meshMaterial);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        mesh.name = 'LoadedModel';
        
        const wireframeMesh = new THREE.Mesh(geometry.clone(), wireframeMaterial);
        wireframeMesh.name = 'LoadedModelWireframe';
        wireframeMesh.visible = showWireframe;
        wireframeMesh.renderOrder = 1;
        
        const group = new THREE.Group();
        group.add(mesh);
        group.add(wireframeMesh);
        group.name = 'LoadedModelGroup';
        
        geometry.computeBoundingBox();
        const box = geometry.boundingBox;
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        
        console.log(`🔍 ${sourceFormat} -> STL Model bounding box:`, {
          min: box.min,
          max: box.max,
          center: center,
          size: size
        });

        const maxDimension = Math.max(size.x, size.y, size.z);
        console.log(`🔍 Max dimension: ${maxDimension}`);
        
        group.position.copy(center).multiplyScalar(-1);
        
        wireframeMeshRef.current = wireframeMesh;
        console.log(`🔍 Wireframe mesh reference stored:`, wireframeMesh);
        
        modelRef.current = group;
        scene.add(group);
        
        console.log(`🔍 ${sourceFormat} -> STL Model added to scene with wireframe overlay, calling fitToView...`);
        fitToView();
        
        wireframeMesh.visible = showWireframe;
        console.log(`🔍 Wireframe visibility set after load: ${showWireframe}`);
        
        console.log(`✅ ${sourceFormat} -> STL model loaded and positioned successfully`);
        toast.success(`${sourceFormat} file loaded as STL! (Assembly structure from ${sourceFormat})`);
      },
      undefined,
      (error) => {
        console.error(`Error loading ${sourceFormat} -> STL:`, error);
        toast.error(`Failed to load ${sourceFormat} as STL`);
        loadPlaceholderModel(scene, `${sourceFormat} (Assembled)`);
      }
    );
  };

  // Load OBJ from URL with source format tracking
  const loadOBJFromUrl = (url, scene, sourceFormat = 'OBJ') => {
    const loader = new OBJLoader();
    loader.load(
      url,
      (object) => {
        console.log(`🔍 ${sourceFormat} -> OBJ loaded:`, object);
        
        let meshCount = 0;
        object.traverse((child) => {
          if (child.isMesh) meshCount++;
        });
        console.log(`🔍 ${sourceFormat} -> OBJ contains ${meshCount} separate meshes`);
        
        const materialProps = material || { 
          color: sourceFormat === 'STEP' ? '#10b981' : sourceFormat === 'IGES' ? '#3b82f6' : '#2563eb',
          metalness: 0.7,
          roughness: 0.1
        };
        
        const validMaterialProps = {
          color: materialProps.color,
          metalness: materialProps.metalness,
          roughness: materialProps.roughness,
          envMapIntensity: 1.0
        };
        
        const meshMaterial = new THREE.MeshStandardMaterial(validMaterialProps);

        const wireframeMaterial = new THREE.MeshBasicMaterial({
          color: 0x00ff00,
          wireframe: true,
          transparent: true,
          opacity: 1.0,
          depthTest: false,
          depthWrite: false
        });

        object.traverse((child) => {
          if (child.isMesh) {
            child.material = meshMaterial;
            child.castShadow = true;
            child.receiveShadow = true;
            
            const wireframeMesh = new THREE.Mesh(child.geometry.clone(), wireframeMaterial);
            wireframeMesh.name = 'LoadedModelWireframe';
            wireframeMesh.visible = showWireframe;
            wireframeMesh.renderOrder = 1;
            object.add(wireframeMesh);
            
            wireframeMeshRef.current = wireframeMesh;
          }
        });

        const box = new THREE.Box3().setFromObject(object);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        
        console.log(`🔍 ${sourceFormat} -> OBJ Model bounding box:`, {
          min: box.min,
          max: box.max,
          center: center,
          size: size
        });

        object.position.copy(center).multiplyScalar(-1);
        
        modelRef.current = object;
        scene.add(object);
        fitToView();
        
        console.log(`✅ ${sourceFormat} -> OBJ model loaded and positioned successfully`);
        toast.success(`${sourceFormat} file loaded as OBJ! (Assembly structure from ${sourceFormat})`);
      },
      undefined,
      (error) => {
        console.error(`Error loading ${sourceFormat} -> OBJ:`, error);
        toast.error(`Failed to load ${sourceFormat} as OBJ`);
        loadPlaceholderModel(scene, `${sourceFormat} (Assembled)`);
      }
    );
  };

  const loadPlaceholderModel = (scene, formatType) => {
    // Create a more informative placeholder for assembled formats
    const isAssembledFormat = formatType.includes('Assembled');
    
    if (isAssembledFormat) {
      // Create a multi-part placeholder to represent assembly
      const group = new THREE.Group();
      
      // Main body (larger cube) - represents main component
      const mainGeometry = new THREE.BoxGeometry(2.5, 1.2, 1.2);
      const mainMaterial = new THREE.MeshStandardMaterial({
        color: '#10b981', // Green for assembled formats
        metalness: 0.8,
        roughness: 0.1
      });
      const mainMesh = new THREE.Mesh(mainGeometry, mainMaterial);
      mainMesh.position.set(0, 0, 0);
      mainMesh.castShadow = true;
      mainMesh.receiveShadow = true;
      group.add(mainMesh);
      
      // Secondary part (smaller cube) - represents sub-assembly
      const secGeometry = new THREE.BoxGeometry(0.8, 0.8, 0.8);
      const secMaterial = new THREE.MeshStandardMaterial({
        color: '#3b82f6', // Blue for secondary part
        metalness: 0.8,
        roughness: 0.1
      });
      const secMesh = new THREE.Mesh(secGeometry, secMaterial);
      secMesh.position.set(1.8, 0.6, 0);
      secMesh.castShadow = true;
      secMesh.receiveShadow = true;
      group.add(secMesh);
      
      // Third part (cylinder) - represents another component
      const thirdGeometry = new THREE.CylinderGeometry(0.3, 0.3, 1.5, 8);
      const thirdMaterial = new THREE.MeshStandardMaterial({
        color: '#f59e0b', // Orange for third part
        metalness: 0.8,
        roughness: 0.1
      });
      const thirdMesh = new THREE.Mesh(thirdGeometry, thirdMaterial);
      thirdMesh.position.set(-1.5, 0, 0);
      thirdMesh.castShadow = true;
      thirdMesh.receiveShadow = true;
      group.add(thirdMesh);
      
      // Add text label (using a simple plane with text texture)
      const canvas = document.createElement('canvas');
      canvas.width = 512;
      canvas.height = 128;
      const context = canvas.getContext('2d');
      context.fillStyle = '#ffffff';
      context.fillRect(0, 0, 512, 128);
      context.fillStyle = '#000000';
      context.font = 'bold 32px Arial';
      context.textAlign = 'center';
      context.fillText(`${formatType}`, 256, 45);
      context.font = '20px Arial';
      context.fillText('Assembly Structure Preserved', 256, 75);
      context.fillText('Download Available Below', 256, 100);
      
      const texture = new THREE.CanvasTexture(canvas);
      const labelGeometry = new THREE.PlaneGeometry(3, 0.75);
      const labelMaterial = new THREE.MeshBasicMaterial({ 
        map: texture, 
        transparent: true,
        side: THREE.DoubleSide
      });
      const labelMesh = new THREE.Mesh(labelGeometry, labelMaterial);
      labelMesh.position.set(0, 2, 0);
      labelMesh.lookAt(0, 2, 1); // Face the camera
      group.add(labelMesh);
      
      group.name = `${formatType}PlaceholderModel`;
      modelRef.current = group;
      scene.add(group);
    } else {
      // Standard single cube for other formats
      const geometry = new THREE.BoxGeometry(1, 1, 1);
      const materialProps = material || { 
        color: document.documentElement.classList.contains('dark') ? '#60a5fa' : '#2563eb', 
        metalness: 0.1, 
        roughness: 0.3 
      };
      const meshMaterial = new THREE.MeshStandardMaterial({
        color: materialProps.color,
        metalness: materialProps.metalness,
        roughness: materialProps.roughness,
      });
      const mesh = new THREE.Mesh(geometry, meshMaterial);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      mesh.name = `${formatType}PlaceholderModel`;
      modelRef.current = mesh;
      scene.add(mesh);
    }
    
    fitToView();
  };

  const fitToView = () => {
    if (!modelRef.current || !cameraRef.current || !controlsRef.current) {
      console.log('🔍 fitToView: Missing refs', {
        model: !!modelRef.current,
        camera: !!cameraRef.current,
        controls: !!controlsRef.current
      });
      return;
    }

    const box = new THREE.Box3().setFromObject(modelRef.current);
    const size = box.getSize(new THREE.Vector3()).length();
    const center = box.getCenter(new THREE.Vector3());

    console.log('🔍 fitToView calculations:', {
      boundingBox: box,
      size: size,
      center: center
    });

    // Ensure minimum distance for very small models
    const distance = Math.max(size * 1.5, 5);
    
    // Position camera at a good viewing angle
    cameraRef.current.position.set(
      center.x + distance,
      center.y + distance * 0.7,
      center.z + distance
    );
    cameraRef.current.lookAt(center);

    console.log('🔍 Camera positioned at:', cameraRef.current.position);
    console.log('🔍 Camera looking at:', center);

    controlsRef.current.target.copy(center);
    controlsRef.current.update();
    
    console.log('✅ fitToView completed');
  };

  const resetView = () => {
    if (!cameraRef.current || !controlsRef.current) return;
    
    cameraRef.current.position.set(5, 5, 5);
    cameraRef.current.lookAt(0, 0, 0);
    controlsRef.current.target.set(0, 0, 0);
    controlsRef.current.update();
    
    if (modelRef.current) {
      fitToView();
    }
  };

  const toggleFullscreen = () => {
    console.log(`🔍 Fullscreen toggle clicked. Current: ${isFullscreen}, Setting to: ${!isFullscreen}`);
    if (onFullscreen) {
      onFullscreen(!isFullscreen);
    } else {
      console.log('🔍 No onFullscreen callback provided');
    }
  };

  const takeScreenshot = () => {
    if (!rendererRef.current) return;
    
    try {
      const canvas = rendererRef.current.domElement;
      const link = document.createElement('a');
      link.download = 'cadscribe-model.png';
      link.href = canvas.toDataURL('image/png');
      link.click();
      toast.success('Screenshot saved!');
    } catch (error) {
      toast.error('Failed to take screenshot');
    }
  };

  const gridStyles = showGrid ? {
    backgroundImage: `
      linear-gradient(hsl(var(--muted-foreground) / 0.3) 1px, transparent 1px),
      linear-gradient(90deg, hsl(var(--muted-foreground) / 0.3) 1px, transparent 1px)
    `,
    backgroundSize: '20px 20px',
    backgroundPosition: 'center center'
  } : {};

  return (
    <div className={`relative bg-muted rounded-lg overflow-hidden ${className}`}>
      <div className="absolute top-4 left-4 z-10 flex items-center space-x-2">
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              onClick={resetView}
              className="bg-background/90 backdrop-blur-sm border-border/50 hover:bg-accent hover:text-accent-foreground"
            >
              <RotateCcw className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Reset View</TooltipContent>
        </Tooltip>
        
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowGrid(!showGrid)}
              className={`bg-background/90 backdrop-blur-sm border-border/50 hover:bg-accent hover:text-accent-foreground ${showGrid ? 'bg-primary text-primary-foreground hover:bg-primary/90' : ''}`}
            >
              <Grid3X3 className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>{showGrid ? 'Hide Grid' : 'Show Grid'}</TooltipContent>
        </Tooltip>
        
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                console.log(`🔍 Wireframe button clicked. Current: ${showWireframe}, Setting to: ${!showWireframe}`);
                setShowWireframe(!showWireframe);
              }}
              className={`bg-background/90 backdrop-blur-sm border-border/50 hover:bg-accent hover:text-accent-foreground ${showWireframe ? 'bg-green-500 text-white hover:bg-green-600' : ''}`}
            >
              <Eye className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>{showWireframe ? 'Hide Wireframe' : 'Show Wireframe'}</TooltipContent>
        </Tooltip>
        
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              onClick={fitToView}
              className="bg-background/90 backdrop-blur-sm border-border/50 hover:bg-accent hover:text-accent-foreground"
            >
              <ZoomIn className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Fit to View</TooltipContent>
        </Tooltip>
        
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setAutoRotate(!autoRotate)}
              className={`bg-background/90 backdrop-blur-sm border-border/50 hover:bg-accent hover:text-accent-foreground ${autoRotate ? 'bg-primary text-primary-foreground hover:bg-primary/90' : ''}`}
            >
              <RotateCw className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>{autoRotate ? 'Stop Rotation' : 'Auto Rotate'}</TooltipContent>
        </Tooltip>
        
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              onClick={takeScreenshot}
              className="bg-background/90 backdrop-blur-sm border-border/50 hover:bg-accent hover:text-accent-foreground"
            >
              <Camera className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Take Screenshot</TooltipContent>
        </Tooltip>
        
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              onClick={toggleFullscreen}
              className="bg-background/90 backdrop-blur-sm border-border/50 hover:bg-accent hover:text-accent-foreground"
            >
              {isFullscreen ? <Minimize className="h-4 w-4" /> : <Maximize className="h-4 w-4" />}
            </Button>
          </TooltipTrigger>
          <TooltipContent>{isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}</TooltipContent>
        </Tooltip>
      </div>

      <div className="absolute bottom-4 right-4 z-10 bg-background/90 backdrop-blur-sm rounded-lg p-3 text-sm border border-border/50 shadow-medium">
        <div className="space-y-1">
          <div className="font-medium text-foreground">Model Info</div>
          <div className="text-muted-foreground">Version: 1.0</div>
          <div className="text-muted-foreground">Engine: FreeCAD</div>
          <div className="text-muted-foreground">Created: Jan 15, 2024</div>
        </div>
      </div>

      <div 
        ref={containerRef} 
        className="w-full h-full min-h-[400px]"
        style={{ 
          cursor: 'grab',
          ...gridStyles
        }}
      />
    </div>
  );
};
