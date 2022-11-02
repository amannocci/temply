//go:build mage
// +build mage

package main

import (
	"bytes"
	"fmt"
	"os"
	"os/exec"

	"github.com/gookit/config/v2"
	"github.com/gookit/config/v2/toml"
	"github.com/magefile/mage/mg"
	"github.com/magefile/mage/sh"
)

type ProjectConf struct {
	Version    string
	Repository string
}

func readProjectConf() (*ProjectConf, error) {
	config.AddDriver(toml.Driver)
	err := config.LoadFiles("pyproject.toml")
	if err != nil {
		return nil, err
	}

	return &ProjectConf{
		Version:    config.String("tool.poetry.version"),
		Repository: config.String("tool.poetry.repository"),
	}, nil
}

func setVersion(version string) error {
	conf, err := readProjectConf()
	if err != nil {
		return err
	}
	currentVersion := conf.Version

	data, err := os.ReadFile("temply/__init__.py")
	if err != nil {
		return err
	}
	output := bytes.Replace(data, []byte(currentVersion), []byte(version), -1)
	if err = os.WriteFile("temply/__init__.py", output, 0644); err != nil {
		return err
	}

	data, err = os.ReadFile("pyproject.toml")
	if err != nil {
		return err
	}
	output = bytes.Replace(data, []byte(currentVersion), []byte(version), -1)
	if err = os.WriteFile("pyproject.toml", output, 0644); err != nil {
		return err
	}
	return nil
}

type Project mg.Namespace

// Update dependencies
func (Project) Upgrade() error {
	fmt.Println("Upgrading project dependencies...")
	return sh.RunV("poetryup", "--latest")
}

type Env mg.Namespace

// Configures environment
func (Env) Configure() error {
	fmt.Println("Install project dependencies...")
	if err := sh.RunV("poetry", "install", "-E", "build"); err != nil {
		return err
	}
	_, err := exec.LookPath("pre-commit")
	if err == nil {
		fmt.Println("Install pre-commit hooks...")
		sh.RunV("pre-commit", "install")
	}
	return nil
}

// Generates project files
func Generate() error {
	mg.Deps(Env.Configure)
	fmt.Println("Generates pyinstaller specs...")
	args := []string{"run", "pyinstaller", "-n", "temply", "--onefile", "--noconfirm"}
	args = append(args, "./bin/temply")
	return sh.RunV("poetry", args...)
}

// Lints the project
func Lint() error {
	mg.Deps(Env.Configure)
	fmt.Println("Linting project...")
	return sh.RunV("poetry", "run", "pylint", "temply")
}

// Formats the project
func Fmt() error {
	mg.Deps(Env.Configure)
	fmt.Println("Formatting project...")
	return sh.RunV("poetry", "run", "black", "temply", "tests")
}

// Builds the project
func Build() error {
	mg.Deps(Env.Configure)
	fmt.Println("Clean previous build")
	if err := os.RemoveAll("./build"); err != nil {
		return err
	}
	if err := os.RemoveAll("./dist"); err != nil {
		return err
	}
	fmt.Println("Create a binary executable")
	return sh.RunV("poetry", "run", "pyinstaller", "cloud-reaper.spec")
}

// Run tests on this project
func Test() error {
	mg.Deps(Env.Configure)
	fmt.Println("Run tests...")
	return sh.RunV("poetry", "run", "pytest")
}

// Create a new release of the project
func Release(releaseVersion string, nextVersion string) error {
	mg.Deps(Env.Configure)

	if err := sh.RunV("git", "checkout", "main"); err != nil {
		return err
	}
	if err := setVersion(releaseVersion); err != nil {
		return err
	}
	if err := sh.RunV("git", "add", "--all"); err != nil {
		return err
	}
	if err := sh.RunV("git", "commit", "-s", "-m", fmt.Sprintf("[Released] temply %s", releaseVersion)); err != nil {
		return err
	}
	if err := sh.RunV("git", "tag", releaseVersion); err != nil {
		return err
	}
	if err := setVersion(nextVersion); err != nil {
		return err
	}
	if err := sh.RunV("git", "add", "--all"); err != nil {
		return err
	}
	if err := sh.RunV("git", "commit", "-s", "-m", "[Updated] Prepare for next iteration"); err != nil {
		return err
	}
	if err := sh.RunV("git", "push"); err != nil {
		return err
	}
	if err := sh.RunV("git", "push", "--tags"); err != nil {
		return err
	}
	return nil
}