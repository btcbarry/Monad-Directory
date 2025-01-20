class MonadAssistant {
    constructor() {
        this.apiUrl = 'http://localhost:8000/chat';
        this.projectsData = null;
    }

    async generateResponse(message) {
        try {
            const lowerMessage = message.toLowerCase();
            
            // Handle calendar/event queries with better context
            if (lowerMessage.includes('event') || 
                lowerMessage.includes('calendar') || 
                lowerMessage.includes('schedule')) {
                
                let response = '';
                
                // Different responses based on specific queries
                if (lowerMessage.includes('next') || lowerMessage.includes('upcoming')) {
                    response = `You can view upcoming events in the Monad Community Calendar. The calendar is regularly updated with:

• Weekly Community Calls
• Developer Updates & AMAs
• Project Launches
• Special Announcements

👉 View the calendar here: https://portdeveloper.github.io/monadcommunitycalendar/

Tip: The calendar shows events in your local timezone automatically!`;
                } 
                else if (lowerMessage.includes('how') || lowerMessage.includes('use')) {
                    response = `Here's how to use the Monad Community Calendar:

1. Visit: https://portdeveloper.github.io/monadcommunitycalendar/
2. Browse events by month or week view
3. Click any event to see full details
4. Events automatically show in your local timezone
5. Add events to your personal calendar with one click

Need to find a specific event? Use the search feature in the calendar interface!`;
                }
                else {
                    response = `The Monad Community Calendar shows all upcoming community events:

• View all events: https://portdeveloper.github.io/monadcommunitycalendar/
• Events are shown in your local timezone
• Regular events include community calls, AMAs, and developer updates
• Click any event for more details

Would you like to know how to use specific calendar features?`;
                }

                return {
                    message: response,
                    suggestions: [
                        "How to use the calendar",
                        "View upcoming events",
                        "When are community calls?",
                        "Find specific event"
                    ]
                };
            }

            // Handle project queries through API (keeping existing functionality)
            const enhancedMessage = await this.enhanceMessage(message);
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: enhancedMessage
                })
            });

            if (!response.ok) {
                throw new Error(`API request failed: ${response.status}`);
            }

            const data = await response.json();
            return {
                message: data.message,
                suggestions: this.getSuggestions(message)
            };

        } catch (error) {
            console.error('Error in generateResponse:', error);
            throw error;
        }
    }

    async enhanceMessage(message) {
        const lowerMessage = message.toLowerCase();
        if (lowerMessage.includes('project') || 
            lowerMessage.includes('directory') ||
            lowerMessage.includes('voted')) {
            const projects = await this.loadProjectsData();
            if (projects) {
                const projectsList = projects.map(p => ({
                    title: p.title,
                    description: p.description,
                    isOnDevnet: p.isOnDevnet
                }));
                return `Context: Available projects: ${JSON.stringify(projectsList, null, 2)}\n\nUser Question: ${message}`;
            }
        }
        return message;
    }

    getSuggestions(message) {
        const lowerMessage = message.toLowerCase();
        if (lowerMessage.includes('project')) {
            return [
                "Show projects on devnet",
                "Most voted projects",
                "Latest projects",
                "Project details"
            ];
        }
        if (lowerMessage.includes('calendar') || lowerMessage.includes('event')) {
            return [
                "How to use the calendar",
                "View upcoming events",
                "When are community calls?",
                "Find specific event"
            ];
        }
        return [];
    }

    async loadProjectsData() {
        if (this.projectsData) {
            return this.projectsData;
        }

        try {
            const response = await fetch('projects.json');
            if (!response.ok) {
                console.error('Projects data fetch failed:', response.status);
                return null;
            }
            this.projectsData = await response.json();
            return this.projectsData;
        } catch (error) {
            console.error('Error loading projects:', error);
            return null;
        }
    }
}