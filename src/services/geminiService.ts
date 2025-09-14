import { GoogleGenerativeAI } from '@google/generative-ai';

// Initialize Gemini AI (you'll need to set your API key)
const GEMINI_API_KEY = process.env.REACT_APP_GEMINI_API_KEY || 'your-gemini-api-key-here';
const genAI = new GoogleGenerativeAI(GEMINI_API_KEY);

export class GeminiService {
  private model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });

  // Enhanced text correction and formatting for transcripts
  async enhanceTranscript(rawText: string): Promise<string> {
    if (!rawText || rawText.trim().length === 0) {
      return rawText;
    }

    try {
      const prompt = `
        Please improve and format this lecture transcript. Make it more readable while preserving the original meaning:
        
        Raw transcript: "${rawText}"
        
        Instructions:
        - Fix grammar and punctuation
        - Add proper sentence breaks
        - Correct obvious speech-to-text errors
        - Maintain the academic tone
        - Keep technical terms intact
        - Add appropriate paragraph breaks
        - Return only the improved text without any additional commentary
      `;

      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      return response.text() || rawText;
    } catch (error) {
      console.error('Error enhancing transcript:', error);
      return rawText; // Return original text if enhancement fails
    }
  }

  // Generate summary of the lecture
  async generateSummary(transcript: string): Promise<string> {
    if (!transcript || transcript.trim().length === 0) {
      return '';
    }

    try {
      const prompt = `
        Create a concise summary of this lecture transcript:
        
        "${transcript}"
        
        Please provide:
        1. Main topics covered
        2. Key points and concepts
        3. Important details to remember
        
        Format as bullet points for easy reading.
      `;

      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      return response.text() || 'Unable to generate summary';
    } catch (error) {
      console.error('Error generating summary:', error);
      return 'Unable to generate summary';
    }
  }

  // Extract key terms and concepts
  async extractKeyTerms(transcript: string): Promise<string[]> {
    if (!transcript || transcript.trim().length === 0) {
      return [];
    }

    try {
      const prompt = `
        Extract the key academic terms, concepts, and important phrases from this lecture transcript:
        
        "${transcript}"
        
        Return only a comma-separated list of key terms without any additional text.
      `;

      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const keyTermsText = response.text() || '';
      
      return keyTermsText
        .split(',')
        .map(term => term.trim())
        .filter(term => term.length > 0)
        .slice(0, 15); // Limit to 15 key terms
    } catch (error) {
      console.error('Error extracting key terms:', error);
      return [];
    }
  }

  // Check if API key is configured
  isConfigured(): boolean {
    return GEMINI_API_KEY !== 'your-gemini-api-key-here' && GEMINI_API_KEY.length > 10;
  }
}

export const geminiService = new GeminiService();