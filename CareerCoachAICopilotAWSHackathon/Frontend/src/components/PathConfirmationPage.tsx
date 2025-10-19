import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { ArrowLeft, ArrowRight, CheckCircle, Clock, Star } from "lucide-react";
import type { Page, UserData } from "../App";
import { ImageWithFallback } from "./figma/ImageWithFallback";

interface PathConfirmationPageProps {
  onNavigate: (page: Page) => void;
  userData: UserData;
  updateUserData: (data: Partial<UserData>) => void;
}

export function PathConfirmationPage({
  onNavigate,
  userData,
}: PathConfirmationPageProps) {
  const selectedPath = userData.selectedPath;

  if (!selectedPath) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary/5 via-accent/5 to-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <h2 className="text-2xl font-bold">No path selected</h2>
          <Button onClick={() => onNavigate("ai-suggestions")}>
            Go back to suggestions
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-accent/5 to-background">
      {/* Header */}
      <header
        className="border-b bg-white/95 backdrop-blur-sm"
        style={{ boxShadow: "0 2px 8px rgba(0,0,0,0.1)" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div
              className="flex items-center space-x-2"
              style={{ cursor: "pointer" }}
              onClick={() => onNavigate("landing")}
            >
              <div className="flex items-center justify-center">
                <ImageWithFallback
                  src="assets/logo.svg"
                  alt="Anblicks AI Career Coaching"
                />
              </div>
              <span className="text-xl font-semibold text-foreground">
                Anblicks Career Coach
              </span>
            </div>
            <Button
              variant="ghost"
              onClick={() => onNavigate("ai-suggestions")}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Suggestions
            </Button>
          </div>
        </div>
      </header>

      <div className="py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header Section */}
          <div className="text-center space-y-6 mb-12">
            <div className="space-y-4">
              <h1 className="text-3xl lg:text-4xl font-bold text-foreground">
                Let's Lock Your Career Path
              </h1>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Confirm your chosen path and we'll create a personalized roadmap
                to help you achieve your goals.
              </p>
            </div>
          </div>

          {/* Selected Path Summary */}
          <Card className="mb-8 border-2 border-primary/20 bg-primary/5">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="space-y-2">
                  <div className="flex items-center space-x-3">
                    <CardTitle className="text-2xl">
                      {selectedPath.title}
                    </CardTitle>
                  </div>
                  <p className="text-muted-foreground text-lg">
                    {selectedPath.description}
                  </p>
                </div>
                <CheckCircle className="w-12 h-12 text-primary" />
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Quick Stats */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white rounded-lg p-4 text-center">
                  <Clock className="w-8 h-8 text-primary mx-auto mb-2" />
                  <div className="text-sm text-muted-foreground">
                    Time to Achieve
                  </div>
                  <div className="font-semibold text-lg">
                    {selectedPath.timeToAchieve}
                  </div>
                </div>
                <div className="bg-white rounded-lg p-4 text-center">
                  <Star className="w-8 h-8 text-yellow-500 mx-auto mb-2" />
                  <div className="text-sm text-muted-foreground">
                    Average Salary
                  </div>
                  <div className="font-semibold text-lg">
                    {selectedPath.averageSalary}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Roadmap Preview */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="text-xl">Your Learning Roadmap</CardTitle>
              <p className="text-muted-foreground">
                A step-by-step guide to achieving your career goals
              </p>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {selectedPath.learningRoadmap.map(
                  (step: string, index: number) => (
                    <div key={index} className="flex items-start space-x-4">
                      <div className="flex-shrink-0">
                        <div className="w-10 h-10 bg-primary/20 rounded-full flex items-center justify-center">
                          <span className="font-semibold text-primary">
                            {index + 1}
                          </span>
                        </div>
                      </div>
                      <div className="pt-2">
                        <h4 className="font-semibold mb-1">
                          Stage {index + 1}
                        </h4>
                        <p className="text-muted-foreground">{step}</p>
                      </div>
                    </div>
                  )
                )}
              </div>
            </CardContent>
          </Card>

          {/* Key Skills */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="text-xl">Skills You'll Develop</CardTitle>
              <p className="text-muted-foreground">
                Essential skills for success in your chosen career path
              </p>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {selectedPath.keySkillsRequired.map(
                  (skill: string, index: number) => (
                    <div
                      key={index}
                      className="bg-white border rounded-lg p-3 text-center"
                    >
                      <span className="font-medium">{skill}</span>
                    </div>
                  )
                )}
              </div>
            </CardContent>
          </Card>

          {/* What Happens Next */}
          <Card className="mb-8 bg-gradient-to-r from-primary/5 to-accent/5">
            <CardHeader>
              <CardTitle className="text-xl">What Happens Next?</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <CheckCircle className="w-6 h-6 text-accent mt-1" />
                  <div>
                    <h4 className="font-semibold">Personalized Dashboard</h4>
                    <p className="text-muted-foreground">
                      Access your career dashboard with progress tracking and
                      resources
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <CheckCircle className="w-6 h-6 text-accent mt-1" />
                  <div>
                    <h4 className="font-semibold">
                      Curated Learning Resources
                    </h4>
                    <p className="text-muted-foreground">
                      Get AI-selected courses, tutorials, and certifications
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <CheckCircle className="w-6 h-6 text-accent mt-1" />
                  <div>
                    <h4 className="font-semibold">AI Mentor Support</h4>
                    <p className="text-muted-foreground">
                      Chat with your AI career mentor for ongoing guidance
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <CheckCircle className="w-6 h-6 text-accent mt-1" />
                  <div>
                    <h4 className="font-semibold">Progress Tracking</h4>
                    <p className="text-muted-foreground">
                      Monitor your learning progress and celebrate milestones
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="flex justify-between items-center">
            <Button
              variant="outline"
              onClick={() => onNavigate("ai-suggestions")}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Choose Different Path
            </Button>

            <Button
              size="lg"
              className="bg-primary hover:bg-primary/90 px-8"
              onClick={() => onNavigate("dashboard")}
            >
              Confirm & Continue
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
