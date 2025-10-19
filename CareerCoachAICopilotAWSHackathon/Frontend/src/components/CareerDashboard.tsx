import { useEffect } from "react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { AppHeader } from "./AppHeader";
import { Footer } from "./Footer";
import { Clock, ArrowRight, Flag } from "lucide-react";
import type { Page, UserData } from "../App";
import useLoader from "../hooks/useLoading";
import { useProfileDetailRoadmap } from "../common/services/userData";

interface CareerDashboardProps {
  onNavigate: (page: Page) => void;
  userData: UserData;
  isAuthenticated?: boolean;
  onLogout?: () => void;
  detailRoadmap: any;
  updateDetailRoadmap: (data: any) => void;
}

export function CareerDashboard({
  onNavigate,
  userData,
  isAuthenticated,
  onLogout,
  detailRoadmap,
  updateDetailRoadmap,
}: CareerDashboardProps) {
  const [showMainLoader, hideMainLoader] = useLoader();
  const selectedPath = userData.selectedPath;

  useEffect(() => {
    let payload = {};
    if (selectedPath) {
      payload = {
        selectedCareerPath: {
          averageSalary: selectedPath.averageSalary,
          description: selectedPath.description,
          keySkillsRequired: selectedPath.keySkillsRequired,
          timeToAchieve: selectedPath.timeToAchieve,
          title: selectedPath.title,
        },
      };
    } else {
      payload = {
        selectedCareerPath: {},
      };
    }
    showMainLoader();
    useProfileDetailRoadmap(payload)
      .then((res) => {
        if (res && res.success) {
          updateDetailRoadmap(res.data);
        }
        hideMainLoader();
      })
      .catch((err) => {
        hideMainLoader();
        console.error(err);
      });
  }, []);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "Advanced":
        return "border-info";
      case "Intermediate":
        return "border-yellow-500";
      case "Beginner":
        return "border-green-500";
      default:
        return "border-gray-300";
    }
  };

  return (
    <div className="min-h-screen bg-background d-flex flex-column">
      <AppHeader
        onNavigate={onNavigate}
        isAuthenticated={isAuthenticated}
        onLogout={onLogout}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Welcome, {userData.first_name}! 🚀
          </h1>
          {selectedPath && (
            <p className="text-xl text-muted-foreground">
              Continue your journey towards becoming a{" "}
              {selectedPath?.title || "professional"}
            </p>
          )}
        </div>

        <div>
          {/* Main Content */}
          <div className="space-y-8">
            {/* Current Path Overview */}
            {selectedPath && (
              <Card className="border-2 border-primary/20 bg-gradient-to-r from-primary/5 to-accent/5">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-2xl">
                        {selectedPath.title}
                      </CardTitle>
                      <p className="text-muted-foreground mt-1">
                        {selectedPath.description}
                      </p>
                    </div>
                  </div>
                </CardHeader>
              </Card>
            )}

            {/* Milestones */}
            <div className="mb-4 border-b">
              <div className="flex items-center space-x-2 text-black">
                <Flag className="w-5 h-5" />
                <h4 className="pt-2 ml-1">Milestones</h4>
              </div>
              <p className="text-muted-foreground">
                Stay on track with your learning goals
              </p>
            </div>

            {/* Milestones list */}
            <div className="space-y-4">
              {detailRoadmap &&
                detailRoadmap.highLevelRoadmap.map(
                  (milestone: any, index: number) => (
                    <div
                      key={index}
                      className={`border-l-4 ${getPriorityColor(
                        milestone.phase
                      )} bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow`}
                    >
                      <div className="space-y-3">
                        <div>
                          <h4 className="font-medium">{milestone.phase}</h4>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Clock className="w-5 h-5 text-muted-foreground" />
                          <span className="text-sm text-muted-foreground">
                            {milestone.duration}
                          </span>
                        </div>
                        <div>
                          <h6>Outcomes:</h6>
                          <div className="flex flex-wrap gap-2">
                            {milestone.outcomes.map(
                              (outcomes: string, index: number) => (
                                <Badge
                                  key={index}
                                  className="text-gray-600 bg-gray-100"
                                >
                                  {outcomes}
                                </Badge>
                              )
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                )}
            </div>
            <Button
              variant="outline"
              className="w-full"
              onClick={() => onNavigate("progress-tracker")}
            >
              View All Milestones
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>
      </div>

      <Footer onNavigate={onNavigate} isAuthenticated={isAuthenticated} />
    </div>
  );
}
