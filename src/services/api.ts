// API service for backend integration with Clerk authentication
const API_BASE_URL = 'http://localhost:5000';

export interface CreateClassData {
  classroom_id: string;
  teacher_clerk_id: string;  // Changed from teacher_code to teacher_clerk_id
  college_name: string;
  subject?: string;
  max_students?: number;
}

export interface UserData {
  clerk_id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'student' | 'teacher';
}

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Clerk-integrated user endpoints
  async getUserByClerkId(clerkId: string) {
    return this.request(`/users/${clerkId}`);
  }

  async updateUserRole(clerkId: string, role: 'student' | 'teacher') {
    return this.request(`/users/${clerkId}/role`, {
      method: 'PUT',
      body: JSON.stringify({ role }),
    });
  }

  // Teacher dashboard with Clerk ID
  async getTeacherDashboard(clerkId: string) {
    return this.request(`/dashboard/teacher/${clerkId}`);
  }

  // Student dashboard with Clerk ID
  async getStudentDashboard(clerkId: string) {
    return this.request(`/dashboard/student/${clerkId}`);
  }

  // Class management with Clerk authentication
  async createClass(data: CreateClassData) {
    return this.request('/create_class', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getClassDetails(classroomId: string) {
    return this.request(`/class_details/${classroomId}`);
  }

  // Generic endpoints
  async createUser(userData: any) {
    return this.request('/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async getUsers() {
    return this.request('/users');
  }

  // Keep existing methods for backwards compatibility
  async createQuiz(quizData: any) {
    return this.request('/quizzes', {
      method: 'POST',
      body: JSON.stringify(quizData),
    });
  }

  async getQuiz(quizId: string) {
    return this.request(`/quizzes/${quizId}`);
  }
}

export const apiService = new ApiService();
export default apiService;