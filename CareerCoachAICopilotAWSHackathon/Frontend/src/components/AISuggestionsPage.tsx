import { useState } from "react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import {
  ArrowLeft,
  ArrowRight,
  Clock,
  DollarSign,
  Sparkles,
  LogOut,
} from "lucide-react";
import type { Page, UserData } from "../App";
import { ImageWithFallback } from "./figma/ImageWithFallback";

interface AISuggestionsPageProps {
  onNavigate: (page: Page) => void;
  userData: UserData;
  onLogout: () => void;
  careerPaths: any[];
  updateUserData: (data: Partial<UserData>) => void;
}

export function AISuggestionsPage({
  onNavigate,
  onLogout,
  userData,
  updateUserData,
  careerPaths,
}: AISuggestionsPageProps) {
  const [selectedPath, setSelectedPath] = useState<any>(null);

  const handleSelectPath = (path: any) => {
    setSelectedPath(path);
    updateUserData({ selectedPath: path });
  };

  const handleContinue = () => {
    if (selectedPath) {
      onNavigate("dashboard");
    }
  };

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
            <div className="d-flex gap-4">
              <Button
                variant="ghost"
                onClick={() => onNavigate("goal-selection")}
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
              <button className="btn btn-outline-danger" onClick={onLogout}>
                <LogOut size={16} className="me-2" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="py-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header Section */}
          <div className="text-center space-y-6 mb-12">
            <div className="flex items-center justify-center space-x-2">
              <Sparkles className="w-8 h-8 text-primary" />
              <h1 className="text-3xl lg:text-4xl font-bold text-foreground">
                Your Personalized Career Suggestions
              </h1>
            </div>
            <div className="bg-white rounded-2xl p-6 border shadow-sm max-w-3xl mx-auto">
              <p className="text-muted-foreground mt-2">
                Based on your background and goal, here are AI-curated career
                paths that match your profile.
              </p>
            </div>
          </div>

          {/* Suggestions Grid */}
          <div className="space-y-6">
            {careerPaths.map((suggestion, index) => (
              <Card
                key={suggestion.id}
                className={`transition-all cursor-pointer border-2 hover:shadow-lg ${
                  selectedPath?.id === suggestion.id
                    ? "border-primary bg-primary/5 shadow-lg"
                    : "border-border hover:border-primary/30"
                }`}
                onClick={() => handleSelectPath(suggestion)}
              >
                <CardHeader className="pb-4">
                  <div className="flex items-start justify-between">
                    <div className="space-y-2 flex-1">
                      <div className="flex items-center space-x-3">
                        <CardTitle className="text-2xl">
                          {suggestion.title}
                        </CardTitle>
                      </div>
                      <p className="text-muted-foreground text-lg">
                        {suggestion.description}
                      </p>
                    </div>
                    <div
                      className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                        selectedPath?.id === suggestion.id
                          ? "border-primary bg-primary"
                          : "border-muted"
                      }`}
                    >
                      {selectedPath?.id === suggestion.id && (
                        <div className="w-3 h-3 bg-white rounded-full"></div>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Quick Stats */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="flex items-center space-x-2">
                      <Clock className="w-5 h-5 text-primary" />
                      <div>
                        <div className="text-sm text-muted-foreground">
                          Time to Achieve
                        </div>
                        <div className="font-semibold">
                          {suggestion.timeToAchieve}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <DollarSign className="w-5 h-5 text-accent" />
                      <div>
                        <div className="text-sm text-muted-foreground">
                          Average Salary
                        </div>
                        <div className="font-semibold">
                          {suggestion.averageSalary}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Key Skills */}
                  <div>
                    <h4 className="font-semibold mb-3">Key Skills Required</h4>
                    <div className="flex flex-wrap gap-2">
                      {suggestion.keySkillsRequired.map(
                        (skill: string, skillIndex: number) => (
                          <Badge
                            key={skillIndex}
                            variant="outline"
                            className="bg-white"
                          >
                            {skill}
                          </Badge>
                        )
                      )}
                    </div>
                  </div>

                  {/* Learning Roadmap Preview */}
                  <div>
                    <h4 className="font-semibold mb-3">Learning Roadmap</h4>
                    <div className="space-y-2">
                      {suggestion.learningRoadmap.map(
                        (step: string, stepIndex: number) => (
                          <div
                            key={stepIndex}
                            className="flex items-center space-x-3"
                          >
                            <div className="w-6 h-6 bg-primary/20 rounded-full flex items-center justify-center text-xs font-semibold text-primary">
                              {stepIndex + 1}
                            </div>
                            <span className="text-sm">{step}</span>
                          </div>
                        )
                      )}
                    </div>
                  </div>

                  {/* AI Recommendation */}
                  <div className="bg-gradient-to-r from-primary/5 to-accent/5 rounded-lg p-4">
                    <div className="flex items-start space-x-3">
                      <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center flex-shrink-0">
                        <Sparkles className="w-4 h-4 text-white" />
                      </div>
                      <div>
                        <h5 className="font-semibold text-sm mb-1">
                          Why AI recommends this path:
                        </h5>
                        <p className="text-sm text-muted-foreground">
                          {suggestion.aiRecommendation.reason}
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="flex justify-between items-center pt-8">
            <Button
              variant="outline"
              onClick={() => onNavigate("goal-selection")}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Refine My Goals
            </Button>

            {selectedPath && (
              <Button
                size="lg"
                className="bg-primary hover:bg-primary/90"
                onClick={handleContinue}
              >
                Lock This Path
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
