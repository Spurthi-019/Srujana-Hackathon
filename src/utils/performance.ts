/**
 * Performance Testing and Monitoring Utilities
 * Provides tools to measure and track app performance
 */

// Web Vitals measurement
export const measureWebVitals = () => {
  if ('web-vitals' in window) {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(console.log);
      getFID(console.log);
      getFCP(console.log);
      getLCP(console.log);
      getTTFB(console.log);
    });
  }
};

// Performance observer for monitoring
export const setupPerformanceMonitoring = () => {
  if ('PerformanceObserver' in window) {
    // Monitor largest contentful paint
    const lcpObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        console.log('LCP:', entry.startTime);
      }
    });
    
    try {
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
    } catch (e) {
      console.warn('LCP observation not supported');
    }

    // Monitor first input delay
    const fidObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if ('processingStart' in entry) {
          console.log('FID:', (entry as any).processingStart - entry.startTime);
        }
      }
    });
    
    try {
      fidObserver.observe({ entryTypes: ['first-input'] });
    } catch (e) {
      console.warn('FID observation not supported');
    }

    // Monitor cumulative layout shift
    const clsObserver = new PerformanceObserver((list) => {
      let clsValue = 0;
      for (const entry of list.getEntries()) {
        if ('hadRecentInput' in entry && 'value' in entry) {
          const layoutShiftEntry = entry as any;
          if (!layoutShiftEntry.hadRecentInput) {
            clsValue += layoutShiftEntry.value;
          }
        }
      }
      if (clsValue > 0) {
        console.log('CLS:', clsValue);
      }
    });
    
    try {
      clsObserver.observe({ entryTypes: ['layout-shift'] });
    } catch (e) {
      console.warn('CLS observation not supported');
    }
  }
};

// Bundle size analyzer
export const analyzeBundleSize = () => {
  if (process.env.NODE_ENV === 'development') {
    console.log('Bundle Analysis:');
    console.log('Main bundle:', document.querySelector('script[src*="main"]')?.getAttribute('src'));
    console.log('Vendor bundle:', document.querySelector('script[src*="vendor"]')?.getAttribute('src'));
    
    // Estimate bundle sizes (rough calculation)
    const scripts = document.querySelectorAll('script[src]');
    scripts.forEach((script, index) => {
      const src = script.getAttribute('src');
      if (src && !src.startsWith('http')) {
        console.log(`Script ${index + 1}:`, src);
      }
    });
  }
};

// Memory usage monitoring
export const monitorMemoryUsage = () => {
  if ('memory' in performance) {
    const memory = (performance as any).memory;
    console.log('Memory Usage:', {
      used: `${Math.round(memory.usedJSHeapSize / 1048576)} MB`,
      total: `${Math.round(memory.totalJSHeapSize / 1048576)} MB`,
      limit: `${Math.round(memory.jsHeapSizeLimit / 1048576)} MB`
    });
  }
};

// Network performance monitoring
export const monitorNetworkPerformance = () => {
  if ('connection' in navigator) {
    const connection = (navigator as any).connection;
    console.log('Network Info:', {
      effectiveType: connection.effectiveType,
      downlink: connection.downlink,
      rtt: connection.rtt,
      saveData: connection.saveData
    });
  }
};

// React render performance tracking
export const trackRenderPerformance = (componentName: string) => {
  return (target: any, propertyKey: string, descriptor: PropertyDescriptor) => {
    const originalMethod = descriptor.value;
    
    descriptor.value = function (...args: any[]) {
      const start = performance.now();
      const result = originalMethod.apply(this, args);
      const end = performance.now();
      
      if (end - start > 16) { // If render takes longer than 16ms (60fps)
        console.warn(`Slow render in ${componentName}.${propertyKey}: ${end - start}ms`);
      }
      
      return result;
    };
    
    return descriptor;
  };
};

// Debounce utility for performance optimization
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number,
  immediate?: boolean
): T => {
  let timeout: NodeJS.Timeout | null = null;
  
  return ((...args: any[]) => {
    const later = () => {
      timeout = null;
      if (!immediate) func(...args);
    };
    
    const callNow = immediate && !timeout;
    
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    
    if (callNow) func(...args);
  }) as T;
};

// Throttle utility for performance optimization
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): T => {
  let inThrottle: boolean;
  
  return ((...args: any[]) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  }) as T;
};

// Initialize all performance monitoring
export const initializePerformanceMonitoring = () => {
  measureWebVitals();
  setupPerformanceMonitoring();
  analyzeBundleSize();
  
  // Set up periodic monitoring
  setInterval(() => {
    monitorMemoryUsage();
    monitorNetworkPerformance();
  }, 30000); // Every 30 seconds
};

// Performance improvement recommendations
export const getPerformanceRecommendations = () => {
  const recommendations = [];
  
  // Check for large DOM
  const domSize = document.querySelectorAll('*').length;
  if (domSize > 1000) {
    recommendations.push('Consider virtualizing large lists to reduce DOM size');
  }
  
  // Check for unused images
  const images = document.querySelectorAll('img');
  const hiddenImages = Array.from(images).filter(img => 
    img.offsetWidth === 0 || img.offsetHeight === 0
  );
  if (hiddenImages.length > 0) {
    recommendations.push(`${hiddenImages.length} hidden images found - consider lazy loading`);
  }
  
  // Check for memory usage
  if ('memory' in performance) {
    const memory = (performance as any).memory;
    const memoryUsage = memory.usedJSHeapSize / memory.jsHeapSizeLimit;
    if (memoryUsage > 0.8) {
      recommendations.push('High memory usage detected - check for memory leaks');
    }
  }
  
  return recommendations;
};