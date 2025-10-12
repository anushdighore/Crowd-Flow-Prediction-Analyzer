"""Device Manager - Minimal GPU Detection (145 lines)"""""""""

import torch

import loggingDevice Manager - Minimal GPU Detection (150 lines MAX)Device Manager - Hardware Abstraction Layer

import yaml

Priority: PyTorch CUDA > CPU fallback

logger = logging.getLogger(__name__)

"""Handles:



class DeviceManager:import torch- CUDA extension detection

    """Minimal device manager for PyTorch GPU detection"""

    import logging- PyTorch GPU detection  

    def __init__(self, config_path=None):

        self.config = self._load_config(config_path)from pathlib import Path- CPU fallback

        self.device_type = "cpu"

        self.device_handle = Noneimport yaml- VRAM monitoring and enforcement (4.5GB hard limit)

        self.device_name = "CPU"

        self.total_vram_mb = 0.0- Device benchmarking

        self.available_vram_mb = 0.0

        self.fallback_triggered = Falselogger = logging.getLogger(__name__)- Real-time memory tracking

        self._detect_device()

        logger.info(f"Device: {self.device_type} ({self.device_name})")

    

    def _load_config(self, config_path):Priority: CUDA Extensions > PyTorch CUDA > CPU

        """Load YAML config or use defaults"""

        if config_path is None:class DeviceManager:

            return {'device': {'preferred': 'cuda', 'max_vram_mb': 4500, 'fallback': True}}

        try:    """Minimal device manager for PyTorch GPU detection"""Author: Crowd Flow Prediction System

            with open(config_path, 'r') as f:

                return yaml.safe_load(f)    Version: 1.0

        except Exception as e:

            logger.warning(f"Config load failed: {e}, using defaults")    def __init__(self, config_path=None):Date: October 09, 2025

            return {'device': {'preferred': 'cuda', 'max_vram_mb': 4500, 'fallback': True}}

            """Initialize with GPU detection""""""

    def _detect_device(self):

        """Detect CUDA GPU or fallback to CPU"""        self.config = self._load_config(config_path)

        if not torch.cuda.is_available():

            logger.info("CUDA not available, using CPU")        self.device_type = "cpu"import torch

            self.device_type = "cpu"

            self.device_handle = torch.device("cpu")        self.device_handle = Noneimport logging

            return

                self.device_name = "CPU"from typing import Dict, List, Optional, Tuple, Literal, Any

        try:

            free_mem, total_mem = torch.cuda.mem_get_info(0)        self.total_vram_mb = 0.0from pathlib import Path

            free_mb = free_mem / (1024**2)

            total_mb = total_mem / (1024**2)        self.available_vram_mb = 0.0from dataclasses import dataclass

            

            if free_mb < 500:        self.fallback_triggered = Falsefrom datetime import datetime

                logger.warning(f"Low VRAM ({free_mb:.0f}MB), falling back to CPU")

                self.device_type = "cpu"        import time

                self.device_handle = torch.device("cpu")

                self.fallback_triggered = True        # Detect deviceimport yaml

                return

                    self._detect_device()

            self.device_type = "cuda"

            self.device_handle = torch.device("cuda:0")        logger.info(f"🖥️  Device: {self.device_type} ({self.device_name})")logger = logging.getLogger(__name__)

            self.device_name = torch.cuda.get_device_name(0)

            self.total_vram_mb = total_mb    

            self.available_vram_mb = free_mb

            logger.info(f"GPU: {self.device_name}, VRAM: {free_mb:.0f}/{total_mb:.0f}MB")    def _load_config(self, config_path):

            

        except Exception as e:        """Load YAML config"""# ================================================================================

            logger.error(f"GPU check failed: {e}, using CPU")

            self.device_type = "cpu"        if config_path is None:# DATA STRUCTURES (Output Contracts)

            self.device_handle = torch.device("cpu")

            self.fallback_triggered = True            # Default config# ================================================================================

    

    def get_device(self):            return {

        """Return torch.device for model placement"""

        if self.device_handle is None:                'device': {@dataclass

            self._detect_device()

        return self.device_handle                    'preferred': 'cuda',class DeviceMetadata:

    

    def get_device_str(self):                    'max_vram_mb': 4500,    """Device information bundle returned to downstream modules"""

        """Return device as string ('cuda' or 'cpu')"""

        return self.device_type                    'fallback': True    device_type: Literal["cuda", "cpu", "cuda_extensions"]

    

    def check_memory(self):                }    device_handle: torch.device

        """Check current VRAM usage"""

        if self.device_type != "cuda":            }    device_name: str

            return {"allocated_mb": 0.0, "reserved_mb": 0.0, "free_mb": 0.0, "total_mb": 0.0}

                    total_vram_mb: float

        try:

            allocated = torch.cuda.memory_allocated(0) / (1024**2)        try:    available_vram_mb: float

            reserved = torch.cuda.memory_reserved(0) / (1024**2)

            free_mem, total_mem = torch.cuda.mem_get_info(0)            with open(config_path, 'r') as f:    allocated_vram_mb: float

            free_mb = free_mem / (1024**2)

            total_mb = total_mem / (1024**2)                return yaml.safe_load(f)    reserved_vram_mb: float

            return {"allocated_mb": allocated, "reserved_mb": reserved, "free_mb": free_mb, "total_mb": total_mb}

        except Exception as e:        except Exception as e:    compute_capability: Optional[str]

            logger.error(f"Memory check failed: {e}")

            return {"error": str(e)}            logger.warning(f"⚠️  Config load failed: {e}, using defaults")    cuda_version: Optional[str]

    

    def force_cpu(self):            return {    fallback_triggered: bool

        """Force CPU fallback"""

        logger.warning("Forcing CPU fallback")                'device': {    extensions_available: bool = False

        self.device_type = "cpu"

        self.device_handle = torch.device("cpu")                    'preferred': 'cuda',

        self.fallback_triggered = True

                        'max_vram_mb': 4500,

    def is_gpu_available(self):

        """Check if GPU is active"""                    'fallback': True@dataclass

        return self.device_type == "cuda"

                }class MemoryStatus:



_device_manager = None            }    """Real-time memory status report"""



        timestamp: str

def get_device_manager(config_path=None):

    """Get or create global DeviceManager"""    def _detect_device(self):    within_limit: bool

    global _device_manager

    if _device_manager is None:        """Detect CUDA GPU or fallback to CPU"""    usage_percentage: float

        _device_manager = DeviceManager(config_path)

    return _device_manager        if not torch.cuda.is_available():    warning_level: Literal["safe", "caution", "critical"]


            logger.info("⚠️  CUDA not available, using CPU")    free_mb: float

            self.device_type = "cpu"    can_allocate_mb: float

            self.device_handle = torch.device("cpu")    allocated_mb: float

            return    reserved_mb: float

            total_mb: float

        # Check VRAM

        try:

            free_mem, total_mem = torch.cuda.mem_get_info(0)class DeviceManager:

            free_mb = free_mem / (1024**2)    """

            total_mb = total_mem / (1024**2)    Hardware Abstraction Layer - Manages device detection, selection, and monitoring

                

            max_vram = self.config['device'].get('max_vram_mb', 4500)    Responsibilities:

                - Detect computational devices (CUDA Extensions → GPU → CPU)

            if free_mb < 500:  # Minimum 500MB needed    - Enforce 4.5GB VRAM hard limit

                logger.warning(f"⚠️  Low VRAM ({free_mb:.0f}MB), falling back to CPU")    - Provide automatic fallback when resources exhausted

                self.device_type = "cpu"    - Monitor real-time memory consumption

                self.device_handle = torch.device("cpu")    - Deliver validated device objects to downstream modules

                self.fallback_triggered = True    """

                return    

                def __init__(self, config_path: Optional[str] = None):

            # GPU available and sufficient VRAM        """

            self.device_type = "cuda"        Initialize DeviceManager

            self.device_handle = torch.device("cuda:0")        

            self.device_name = torch.cuda.get_device_name(0)        Args:

            self.total_vram_mb = total_mb            config_path: Path to device_config.yaml (optional)

            self.available_vram_mb = free_mb        """

                    self.config: Dict[str, Dict[str, Any]] = self._load_config(config_path)

            logger.info(f"✅ GPU: {self.device_name}")        self.available_devices: List[str] = []

            logger.info(f"📊 VRAM: {free_mb:.0f}/{total_mb:.0f}MB")        self.device_info: Dict[str, Dict[str, Any]] = {}

                    self.current_device: Optional[str] = None

        except Exception as e:        self.benchmark_cache: Dict[str, Dict[str, Any]] = {}

            logger.error(f"❌ GPU check failed: {e}, using CPU")        self._fallback_triggered: bool = False

            self.device_type = "cpu"        self._vram_limit_mb: float = self.config['device']['max_vram_mb']

            self.device_handle = torch.device("cpu")        

            self.fallback_triggered = True        # Detect devices on initialization

            self._detect_devices()

    def get_device(self):        

        """Return torch.device for model placement"""        # Select best device

        if self.device_handle is None:        self.current_device = self.get_best_device()

            self._detect_device()        

        return self.device_handle        # Optional benchmarking

            if self.config['device'].get('benchmark_on_init', False):

    def get_device_str(self):            logger.info("Running device benchmark...")

        """Return device as string ('cuda' or 'cpu')"""            self.benchmark_device()

        return self.device_type        

            if self.config['monitoring']['log_device_info']:

    def check_memory(self):            self._log_device_info()

        """Check current VRAM usage (GPU only)"""    

        if self.device_type != "cuda":    def _load_config(self, config_path: Optional[str]) -> Dict[str, Dict[str, Any]]:

            return {        """Load device configuration from YAML"""

                "allocated_mb": 0.0,        if config_path is None:

                "reserved_mb": 0.0,            # Default path relative to this file

                "free_mb": 0.0,            config_path_obj = Path(__file__).parent.parent.parent / "config" / "device_config.yaml"

                "total_mb": 0.0            config_path = str(config_path_obj)

            }        

                try:

        try:            with open(config_path, 'r', encoding='utf-8') as f:

            allocated = torch.cuda.memory_allocated(0) / (1024**2)                config = yaml.safe_load(f)

            reserved = torch.cuda.memory_reserved(0) / (1024**2)            logger.info(f"Loaded device config from {config_path}")

            free_mem, total_mem = torch.cuda.mem_get_info(0)            

            free_mb = free_mem / (1024**2)            # Validate critical settings

            total_mb = total_mem / (1024**2)            self._validate_config(config)

                        return config

            return {        except Exception as e:

                "allocated_mb": allocated,            logger.warning(f"Could not load device config: {e}. Using defaults.")

                "reserved_mb": reserved,            return self._get_default_config()

                "free_mb": free_mb,    

                "total_mb": total_mb    def _validate_config(self, config: Dict[str, Any]) -> None:

            }        """

        except Exception as e:        Validate configuration and clamp invalid values

            logger.error(f"Memory check failed: {e}")        

            return {"error": str(e)}        Error Handling: Scenario 6 & 7 from spec

            """

    def force_cpu(self):        device_pref = config.get('device', {}).get('preferred', 'auto')

        """Force CPU fallback"""        if device_pref not in ['auto', 'cuda', 'cpu']:

        logger.warning("🔄 Forcing CPU fallback")            logger.error(f"Invalid device preference '{device_pref}', defaulting to 'auto'")

        self.device_type = "cpu"            config['device']['preferred'] = 'auto'

        self.device_handle = torch.device("cpu")        

        self.fallback_triggered = True        # Scenario 7: VRAM limit exceeds physical capacity

            if torch.cuda.is_available():

    def is_gpu_available(self):            total_vram_mb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 2)

        """Quick check if GPU is active"""            requested_limit = config.get('device', {}).get('max_vram_mb', 4500)

        return self.device_type == "cuda"            

            # Clamp to 80% of physical VRAM

            max_safe_limit = total_vram_mb * 0.80

# Global singleton instance            if requested_limit > max_safe_limit:

_device_manager = None                logger.warning(

                    f"VRAM limit {requested_limit}MB exceeds safe capacity "

                    f"(80% of {total_vram_mb:.0f}MB). Clamping to {max_safe_limit:.0f}MB"

def get_device_manager(config_path=None):                )

    """Get or create global DeviceManager instance"""                config['device']['max_vram_mb'] = int(max_safe_limit)

    global _device_manager    

    if _device_manager is None:    def _get_default_config(self) -> Dict[str, Dict[str, Any]]:

        _device_manager = DeviceManager(config_path)        """Return default configuration if YAML not found"""

    return _device_manager        return {

            'device': {
                'preferred': 'auto',
                'fallback': True,
                'max_vram_mb': 4500,
                'min_free_vram_mb': 1000,
                'benchmark_on_init': False,
                'cache_benchmark': True
            },
            'cuda': {
                'use_extensions': True,
                'mixed_precision': False,
                'memory_fraction': 0.9,
                'use_cuda_graphs': False
            },
            'cpu': {
                'num_threads': 0,
                'use_mkl': True
            },
            'monitoring': {
                'log_device_info': True,
                'track_vram': True,
                'log_performance': True
            }
        }
    
    def _detect_devices(self) -> None:
        """
        PHASE 1: Initial Detection
        
        Detects available devices in priority order:
        1. CUDA Extensions (custom CUDA kernels)
        2. Standard CUDA/GPU
        3. CPU (always available)
        """
        self.available_devices = []
        self.device_info = {}
        
        # Check for CUDA
        if torch.cuda.is_available():
            try:
                # Check for CUDA extensions (mamba-ssm, etc.)
                cuda_extensions_available = self._check_cuda_extensions()
                
                if cuda_extensions_available and self.config['cuda']['use_extensions']:
                    device_name = 'cuda_extension'
                    self.available_devices.append(device_name)
                    self.device_info[device_name] = self._get_cuda_info()
                    self.device_info[device_name]['extensions'] = True
                    logger.info("✅ CUDA extensions detected")
                
                # Standard CUDA/GPU
                device_name = 'cuda'
                self.available_devices.append(device_name)
                self.device_info[device_name] = self._get_cuda_info()
                self.device_info[device_name]['extensions'] = False
                logger.info(f"✅ CUDA detected: {self.device_info[device_name]['name']}")
                
            except Exception as e:
                logger.error(f"Error detecting CUDA: {e}")
                # Fall through to CPU
        else:
            logger.info("⚠️  CUDA not available (Error Scenario 1: CUDA unavailability)")
        
        # CPU always available
        device_name = 'cpu'
        self.available_devices.append(device_name)
        self.device_info[device_name] = self._get_cpu_info()
        logger.info("✅ CPU available")
    
    def _check_cuda_extensions(self) -> bool:
        """
        Check if CUDA extensions are available
        
        Returns:
            True if custom CUDA extensions installed and functional
        """
        try:
            # Try importing mamba-ssm (common CUDA extension)
            import mamba_ssm  # type: ignore
            return True
        except ImportError:
            return False
    
    def _get_cuda_info(self) -> Dict[str, Any]:
        """
        Get comprehensive CUDA device information
        
        Returns:
            Dictionary with GPU specs, memory stats, compute capability
        """
        if not torch.cuda.is_available():
            return {}
        
        props = torch.cuda.get_device_properties(0)
        
        # Get memory info in MB
        total_memory_mb = props.total_memory / (1024 ** 2)
        allocated_memory_mb = torch.cuda.memory_allocated(0) / (1024 ** 2)
        reserved_memory_mb = torch.cuda.memory_reserved(0) / (1024 ** 2)
        free_memory_mb = total_memory_mb - allocated_memory_mb
        
        return {
            'type': 'cuda',
            'name': props.name,
            'compute_capability': f"{props.major}.{props.minor}",
            'total_memory_mb': round(total_memory_mb, 2),
            'total_memory_gb': round(total_memory_mb / 1024, 2),
            'allocated_memory_mb': round(allocated_memory_mb, 3),
            'allocated_memory_gb': round(allocated_memory_mb / 1024, 3),
            'reserved_memory_mb': round(reserved_memory_mb, 3),
            'reserved_memory_gb': round(reserved_memory_mb / 1024, 3),
            'free_memory_mb': round(free_memory_mb, 2),
            'free_memory_gb': round(free_memory_mb / 1024, 2),
            'multi_processors': props.multi_processor_count,
            'cuda_version': torch.version.cuda,
            'cudnn_version': torch.backends.cudnn.version() if torch.backends.cudnn.is_available() else None,
        }
    
    def _get_cpu_info(self) -> Dict[str, Any]:
        """
        Get CPU device information
        
        Returns:
            Dictionary with CPU specs and threading info
        """
        return {
            'type': 'cpu',
            'name': 'CPU',
            'threads': torch.get_num_threads(),
            'mkl_available': torch.backends.mkl.is_available() if hasattr(torch.backends, 'mkl') else False,
        }
    
    def get_best_device(self) -> str:
        """
        PHASE 3: Device Selection Decision
        
        Get best available device based on priority and VRAM availability
        
        Priority: cuda_extension > cuda > cpu
        
        Returns:
            Device string ('cuda', 'cpu')
            
        Raises:
            RuntimeError: If preferred device unavailable and fallback disabled
        """
        preferred = self.config['device']['preferred']
        
        # Scenario A & B: CUDA available with sufficient VRAM
        if preferred == 'auto' or preferred == 'cuda':
            # Try CUDA extensions first
            if 'cuda_extension' in self.available_devices:
                if self._check_vram_available():
                    logger.info("Selected: CUDA with extensions")
                    return 'cuda'  # Return 'cuda' as PyTorch device string
                else:
                    logger.warning("CUDA extensions available but insufficient VRAM")
            
            # Try standard CUDA
            if 'cuda' in self.available_devices:
                if self._check_vram_available():
                    logger.info("Selected: Standard CUDA")
                    return 'cuda'
                else:
                    # Scenario C: VRAM exceeded - try cache clearing
                    logger.warning("VRAM limit exceeded, attempting cache clear...")
                    if self._attempt_vram_recovery():
                        logger.info("VRAM recovered, using CUDA")
                        return 'cuda'
                    else:
                        logger.warning("VRAM recovery failed")
            
            # Scenario D & Error Scenario 1: No CUDA or VRAM exhausted - fallback to CPU
            if self.config['device']['fallback']:
                self._fallback_triggered = True
                logger.warning(
                    "⚠️  CUDA not available or VRAM exceeded (Scenario 1 & 2), "
                    "falling back to CPU"
                )
                return 'cpu'
            else:
                raise RuntimeError(
                    "CUDA requested but not available or VRAM exhausted, "
                    "and fallback disabled"
                )
        
        elif preferred == 'cpu':
            logger.info("CPU explicitly requested")
            return 'cpu'
        
        else:
            # Specific device requested
            if preferred in self.available_devices:
                return preferred
            elif self.config['device']['fallback']:
                self._fallback_triggered = True
                logger.warning(
                    f"Requested device '{preferred}' not available, "
                    f"falling back to CPU"
                )
                return 'cpu'
            else:
                raise RuntimeError(
                    f"Device '{preferred}' not available and fallback disabled"
                )
    
    def _check_vram_available(self) -> bool:
        """
        PHASE 2: VRAM Feasibility Assessment
        
        Check if sufficient VRAM is available within 4.5GB hard limit
        
        Returns:
            True if VRAM available and within limits, False otherwise
        """
        if not torch.cuda.is_available():
            return False
        
        max_vram_mb = self._vram_limit_mb  # 4.5GB enforcement
        min_free_mb = self.config['device'].get('min_free_vram_mb', 1000)
        
        # Get current VRAM usage using PyTorch CUDA memory APIs
        allocated_mb = torch.cuda.memory_allocated(0) / (1024 ** 2)
        reserved_mb = torch.cuda.memory_reserved(0) / (1024 ** 2)
        total_mb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 2)
        
        # Calculate available VRAM: total - (allocated + reserved)
        available_vram = total_mb - (allocated_mb + reserved_mb)
        
        # Scenario 2: Insufficient VRAM
        if allocated_mb > max_vram_mb:
            logger.warning(
                f"❌ VRAM limit exceeded: {allocated_mb:.0f}MB allocated "
                f"> {max_vram_mb:.0f}MB limit (Scenario 2)"
            )
            return False
        
        # Check minimum free VRAM requirement
        if available_vram < min_free_mb:
            logger.warning(
                f"⚠️  Insufficient free VRAM: {available_vram:.0f}MB free, "
                f"need {min_free_mb}MB"
            )
            return False
        
        # Scenario 4: Operating near VRAM limit (90-100% of 4.5GB)
        usage_percent = (allocated_mb / max_vram_mb) * 100
        if usage_percent >= 90:
            logger.warning(
                f"⚠️  Operating near VRAM limit: {usage_percent:.1f}% "
                f"({allocated_mb:.0f}MB / {max_vram_mb:.0f}MB) - Scenario 4"
            )
            # Continue but flag for monitoring
        
        return True
    
    def _attempt_vram_recovery(self) -> bool:
        """
        Scenario 2 & 3: Attempt to recover VRAM by clearing cache
        
        Returns:
            True if sufficient VRAM recovered, False otherwise
        """
        if not torch.cuda.is_available():
            return False
        
        try:
            # Clear PyTorch CUDA cache
            logger.info("Clearing CUDA cache...")
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            
            # Re-check VRAM availability
            time.sleep(0.5)  # Brief pause for cache clearing to complete
            return self._check_vram_available()
            
        except Exception as e:
            logger.error(f"Error during VRAM recovery: {e}")
            return False
    
    def get_device_metadata(self, device: Optional[str] = None) -> DeviceMetadata:
        """
        Get comprehensive device metadata bundle (OUTPUT CONTRACT)
        
        This is the primary interface for downstream modules to obtain
        validated device information.
        
        Args:
            device: Device name (None = current device)
            
        Returns:
            DeviceMetadata object with all device information
        """
        if device is None:
            device = self.current_device
        
        if device == 'cuda' and torch.cuda.is_available():
            info = self._get_cuda_info()
            has_extensions = 'cuda_extension' in self.available_devices
            
            return DeviceMetadata(
                device_type="cuda_extensions" if has_extensions else "cuda",
                device_handle=torch.device('cuda'),
                device_name=info['name'],
                total_vram_mb=info['total_memory_mb'],
                available_vram_mb=info['free_memory_mb'],
                allocated_vram_mb=info['allocated_memory_mb'],
                reserved_vram_mb=info['reserved_memory_mb'],
                compute_capability=info['compute_capability'],
                cuda_version=info['cuda_version'],
                fallback_triggered=self._fallback_triggered,
                extensions_available=has_extensions
            )
        else:
            # CPU device
            return DeviceMetadata(
                device_type="cpu",
                device_handle=torch.device('cpu'),
                device_name="CPU",
                total_vram_mb=0.0,
                available_vram_mb=0.0,
                allocated_vram_mb=0.0,
                reserved_vram_mb=0.0,
                compute_capability=None,
                cuda_version=None,
                fallback_triggered=self._fallback_triggered,
                extensions_available=False
            )
    
    def get_memory_status(self) -> MemoryStatus:
        """
        PHASE 5: Monitoring Loop
        
        Get real-time memory status report for VRAM monitoring
        
        Returns:
            MemoryStatus object with current memory state
        """
        if not torch.cuda.is_available():
            # Return empty status for CPU
            return MemoryStatus(
                timestamp=datetime.now().isoformat(),
                within_limit=True,
                usage_percentage=0.0,
                warning_level="safe",
                free_mb=0.0,
                can_allocate_mb=0.0,
                allocated_mb=0.0,
                reserved_mb=0.0,
                total_mb=0.0
            )
        
        # Get current VRAM stats
        allocated_mb = torch.cuda.memory_allocated(0) / (1024 ** 2)
        reserved_mb = torch.cuda.memory_reserved(0) / (1024 ** 2)
        total_mb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 2)
        free_mb = total_mb - allocated_mb - reserved_mb
        
        # Calculate against 4.5GB limit
        limit_mb = self._vram_limit_mb
        usage_percent = (allocated_mb / limit_mb) * 100
        within_limit = allocated_mb <= limit_mb
        
        # Determine warning level
        if usage_percent >= 95:
            warning_level = "critical"
        elif usage_percent >= 90:
            warning_level = "caution"
        else:
            warning_level = "safe"
        
        # Calculate allocatable memory (remaining under limit)
        can_allocate_mb = max(0, limit_mb - allocated_mb)
        
        return MemoryStatus(
            timestamp=datetime.now().isoformat(),
            within_limit=within_limit,
            usage_percentage=round(usage_percent, 2),
            warning_level=warning_level,
            free_mb=round(free_mb, 2),
            can_allocate_mb=round(can_allocate_mb, 2),
            allocated_mb=round(allocated_mb, 2),
            reserved_mb=round(reserved_mb, 2),
            total_mb=round(total_mb, 2)
        )
    
    def can_allocate_model(self, model_size_mb: float) -> Tuple[bool, str]:
        """
        Integration Contract: Check if device can accommodate model
        
        Used by ModelManager to validate model loading feasibility.
        
        Args:
            model_size_mb: Predicted model size in MB
            
        Returns:
            Tuple of (can_load: bool, message: str)
        """
        if self.current_device == 'cpu':
            return True, "CPU has sufficient system RAM"
        
        if not torch.cuda.is_available():
            return False, "CUDA not available"
        
        memory_status = self.get_memory_status()
        
        if not memory_status.within_limit:
            return False, f"Already exceeding VRAM limit ({memory_status.usage_percentage:.1f}%)"
        
        if model_size_mb > memory_status.can_allocate_mb:
            remaining_mb = memory_status.can_allocate_mb
            return False, (
                f"Insufficient VRAM: Model requires {model_size_mb:.0f}MB, "
                f"only {remaining_mb:.0f}MB available within {self._vram_limit_mb}MB limit"
            )
        
        # Check if allocation would trigger warning level
        projected_usage = memory_status.allocated_mb + model_size_mb
        projected_percent = (projected_usage / self._vram_limit_mb) * 100
        
        if projected_percent >= 90:
            message = (
                f"Can load but will use {projected_percent:.1f}% of VRAM limit. "
                f"Remaining: {memory_status.can_allocate_mb - model_size_mb:.0f}MB"
            )
        else:
            message = (
                f"Sufficient VRAM: {memory_status.can_allocate_mb:.0f}MB available, "
                f"{memory_status.can_allocate_mb - model_size_mb:.0f}MB remaining after load"
            )
        
        return True, message
    
    def force_refresh(self) -> None:
        """
        Runtime override: Force refresh of device detection
        
        Re-evaluates device availability and VRAM status.
        Useful after external operations that may have changed device state.
        """
        logger.info("Forcing device refresh...")
        self._detect_devices()
        self.current_device = self.get_best_device()
        logger.info(f"Device refresh complete. Current device: {self.current_device}")
    
    def get_device_info(self, device: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a device (legacy compatibility method)
        
        Args:
            device: Device name (None = current device)
            
        Returns:
            Device info dictionary
        """
        if device is None:
            device = self.current_device
        
        if device == 'cuda' and 'cuda_extension' in self.available_devices:
            # Return info with extension flag
            result = self.device_info.get('cuda_extension', {})
            return result if result else {}
        
        result = self.device_info.get(device or 'cpu', {})
        return result if result else {}
    
    def set_device(self, device: str) -> None:
        """
        Set current device
        
        Args:
            device: Device string ('cuda', 'cpu')
        """
        if device not in self.available_devices and device != 'cuda':
            raise ValueError(f"Device '{device}' not available. Available: {self.available_devices}")
        
        self.current_device = device
        logger.info(f"Device set to: {device}")
    
    def benchmark_device(self, device: Optional[str] = None, matrix_size: int = 2000) -> Dict[str, Any]:
        """
        PHASE 4: Device Warmup (Optional)
        
        Benchmark device performance with matrix multiplication
        
        Args:
            device: Device to benchmark (None = current device)
            matrix_size: Size of test matrices
            
        Returns:
            Benchmark results (time in seconds, throughput in GFLOPS)
        """
        import time
        
        if device is None:
            device = self.current_device
        
        # Check cache
        cache_key = f"{device}_{matrix_size}"
        if self.config['device']['cache_benchmark'] and cache_key in self.benchmark_cache:
            logger.info(f"Using cached benchmark for {device}")
            return self.benchmark_cache[cache_key]
        
        logger.info(f"Benchmarking {device} with {matrix_size}x{matrix_size} matrices...")
        
        # Create test tensors
        a = torch.randn(matrix_size, matrix_size)
        b = torch.randn(matrix_size, matrix_size)
        
        if device == 'cuda':
            a = a.cuda()
            b = b.cuda()
            # Warmup
            _ = torch.matmul(a, b)
            torch.cuda.synchronize()
        
        # Benchmark
        times: List[float] = []
        for _ in range(5):
            start = time.time()
            _ = torch.matmul(a, b)
            if device == 'cuda':
                torch.cuda.synchronize()
            times.append(time.time() - start)
        
        avg_time = sum(times[1:]) / 4  # Skip first run
        
        result: Dict[str, Any] = {
            'device': device,
            'matrix_size': matrix_size,
            'avg_time_sec': round(avg_time, 4),
            'throughput_gflops': round((2 * matrix_size ** 3) / (avg_time * 1e9), 2)
        }
        
        # Cache result
        if self.config['device']['cache_benchmark']:
            self.benchmark_cache[cache_key] = result
        
        logger.info(f"Benchmark result: {avg_time:.4f}s, {result['throughput_gflops']:.2f} GFLOPS")
        return result
    
    def get_vram_usage(self) -> Dict[str, float]:
        """
        Get current VRAM usage statistics
        
        Returns:
            VRAM usage info dictionary (only if CUDA available)
        """
        if not torch.cuda.is_available():
            return {}
        
        allocated_mb = torch.cuda.memory_allocated(0) / (1024 ** 2)
        reserved_mb = torch.cuda.memory_reserved(0) / (1024 ** 2)
        total_mb = float(torch.cuda.get_device_properties(0).total_memory / (1024 ** 2))
        free_mb = float(total_mb - allocated_mb)
        
        return {
            'allocated_mb': round(allocated_mb, 2),
            'reserved_mb': round(reserved_mb, 2),
            'free_mb': round(free_mb, 2),
            'total_mb': round(total_mb, 2),
            'usage_percent': round((allocated_mb / total_mb) * 100, 1)
        }
    
    def _log_device_info(self):
        """Log device information"""
        logger.info("=" * 70)
        logger.info("🎮 Device Manager Initialized")
        logger.info("=" * 70)
        logger.info(f"Current device: {self.current_device}")
        logger.info(f"Available devices: {self.available_devices}")
        
        if self.current_device:
            info = self.get_device_info()
            if info.get('type') == 'cuda':
                logger.info(f"GPU: {info['name']}")
                logger.info(f"VRAM: {info['total_memory_gb']:.2f} GB total, {info['free_memory_gb']:.2f} GB free")
                logger.info(f"CUDA: {info['cuda_version']}")
            else:
                logger.info(f"Using CPU with {info['threads']} threads")
        
        logger.info("=" * 70)


# Singleton instance
_device_manager_instance: Optional[DeviceManager] = None


def get_device_manager(config_path: Optional[str] = None) -> DeviceManager:
    """
    Get singleton DeviceManager instance
    
    Args:
        config_path: Path to device config (only used on first call)
        
    Returns:
        DeviceManager instance
    """
    global _device_manager_instance
    
    if _device_manager_instance is None:
        _device_manager_instance = DeviceManager(config_path)
    
    return _device_manager_instance
