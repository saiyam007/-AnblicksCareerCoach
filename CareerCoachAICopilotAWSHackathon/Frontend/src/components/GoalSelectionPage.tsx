import { useState, useEffect, FormEvent } from "react";
import { Sparkles, CheckCircle, LogOut } from "lucide-react";
import type { Page, UserData } from "../App";
import {
  useProfileQuestions,
  useProfileRoadMap,
} from "../common/services/userData";
import useLoader from "../hooks/useLoading";
import { Card, CardContent, CardHeader } from "./ui/card";
import { ImageWithFallback } from "./figma/ImageWithFallback";

interface GoalSelectionPageProps {
  onNavigate: (page: Page) => void;
  onLogout: () => void;
  userData: UserData;
  updateUserData: (data: Partial<UserData>) => void;
  updateCareerPaths: (data: any) => void;
}

interface Question {
  id: string;
  text: string;
  type?: "yes" | "no"; // optional initially
}

export function GoalSelectionPage({
  onNavigate,
  userData,
  onLogout,
  updateCareerPaths,
}: GoalSelectionPageProps) {
  const [showMainLoader, hideMainLoader] = useLoader();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    showMainLoader();
    useProfileQuestions()
      .then((res) => {
        if (res && res.success) {
          setQuestions(res.data.questions);
        }
        hideMainLoader();
      })
      .catch((err) => {
        hideMainLoader();
        console.error(err);
      });
  }, []);

  const handleChange = (id: string, value: "yes" | "no") => {
    setQuestions((prev) =>
      prev.map((q) => (q.id === id ? { ...q, type: value } : q))
    );
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    // Check if all questions are answered
    const allAnswered = questions.every((q) => q.type);
    if (!allAnswered) {
      setError("Please answer all questions before submitting.");
      return;
    }

    setError("");
    showMainLoader();
    useProfileRoadMap(questions)
      .then((res) => {
        if (res && res.success) {
          updateCareerPaths(res.data.careerPaths);
          onNavigate("ai-suggestions");
        }
        hideMainLoader();
      })
      .catch((err) => {
        hideMainLoader();
        console.error(err);
      });
  };

  return (
    <div className="min-h-screen bg-light">
      {/* Header with Bootstrap styling and box-shadow */}
      <header
        className="bg-white border-bottom sticky-top"
        style={{ boxShadow: "0 2px 8px rgba(0,0,0,0.1)" }}
      >
        <div className="container">
          <div className="d-flex justify-content-between align-items-center py-3">
            <div
              className="d-flex align-items-center gap-2"
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
            <button className="btn btn-outline-danger" onClick={onLogout}>
              <LogOut size={16} className="me-2" />
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="container py-4" style={{ maxWidth: "900px" }}>
        <form onSubmit={handleSubmit}>
          {questions.length > 0 ? (
            <>
              {questions.map((q, index) => (
                <Card key={q.id} style={{ marginBottom: "20px" }}>
                  {/* 🔹 Display question number */}
                  <CardHeader>
                    <strong>
                      {index + 1}. {q.text}
                    </strong>
                  </CardHeader>

                  <CardContent>
                    <label style={{ marginRight: "15px" }}>
                      <input
                        className="form-check-input"
                        type="radio"
                        name={q.id}
                        value="yes"
                        onChange={() => handleChange(q.id, "yes")}
                        checked={q.type === "yes"}
                      />{" "}
                      Yes
                    </label>

                    <label>
                      <input
                        className="form-check-input"
                        type="radio"
                        name={q.id}
                        value="no"
                        onChange={() => handleChange(q.id, "no")}
                        checked={q.type === "no"}
                      />{" "}
                      No
                    </label>
                  </CardContent>
                </Card>
              ))}

              {error && <p style={{ color: "red" }}>{error}</p>}

              <div className="text-end">
                <button
                  type="submit"
                  className="btn flex-fill text-white"
                  style={{ backgroundColor: "var(--primary)" }}
                >
                  Submit
                  <CheckCircle className="ms-2" size={20} />
                </button>
              </div>
            </>
          ) : (
            [...Array(5)].map((_, idx) => (
              <Card key={idx} style={{ marginBottom: "20px" }}>
                <CardHeader></CardHeader>
                <CardContent></CardContent>
              </Card>
            ))
          )}
        </form>

        {/* Info Card */}
        <div
          className="card border-0 mt-4"
          style={{ backgroundColor: "rgba(0, 203, 194, 0.1)" }}
        >
          <div className="card-body text-center">
            <Sparkles
              size={32}
              className="mb-2"
              style={{ color: "var(--accent)" }}
            />
            <h6 className="fw-semibold">AI-Powered Career Guidance</h6>
            <p className="text-muted small mb-0">
              Once you're ready, I'll create a personalized roadmap for your
              career journey.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
