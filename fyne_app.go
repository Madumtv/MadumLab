package main

import (
    "fyne.io/fyne/v2/app"
    "fyne.io/fyne/v2/container"
    "fyne.io/fyne/v2/dialog"
    "fyne.io/fyne/v2/storage"
    "fyne.io/fyne/v2/widget"
    "fyne.io/fyne/v2"
    "image"
    "image/png"
    "os"
    "path/filepath"
    "strings"
)

type Item struct {
    Path  string
    IsDir bool
}

func parseTree(text string) []Item {
    var items []Item
    var parents []string
    lines := strings.Split(text, "\n")
    for _, line := range lines {
        if strings.TrimSpace(line) == "" {
            continue
        }
        indent := strings.Count(line, "    ")
        name := strings.TrimSpace(strings.TrimLeft(line, " │"))
        isDir := strings.HasSuffix(name, "/")
        if isDir {
            name = strings.TrimSuffix(name, "/")
        }
        if indent > len(parents) {
            indent = len(parents)
        }
        parents = parents[:indent]
        rel := filepath.Join(append(parents, name)...)
        items = append(items, Item{rel, isDir})
        if isDir {
            parents = append(parents, name)
        }
    }
    return items
}

func main() {
    a := app.New()
    w := a.NewWindow("MadumLab Fyne")

    destEntry := widget.NewEntry()
    asciiEntry := widget.NewMultiLineEntry()
    asciiEntry.SetPlaceHolder("folder/\n    file.txt")
    chooseDest := widget.NewButton("Choose", func() {
        dialog.NewFolderOpen(func(lu fyne.ListableURI, err error) {
            if lu != nil {
                destEntry.SetText(lu.Path())
            }
        }, w).Show()
    })
    genBtn := widget.NewButton("Generate", func() {
        base := destEntry.Text
        for _, it := range parseTree(asciiEntry.Text) {
            full := filepath.Join(base, it.Path)
            if it.IsDir {
                os.MkdirAll(full, 0755)
            } else {
                os.MkdirAll(filepath.Dir(full), 0755)
                os.WriteFile(full, []byte{}, 0644)
            }
        }
        dialog.ShowInformation("OK", "Done", w)
    })
    treeTab := container.NewVBox(
        widget.NewLabel("Dest"), container.NewHBox(destEntry, chooseDest),
        widget.NewLabel("Tree"), asciiEntry, genBtn)

    imgLabel := widget.NewLabel("(none)")
    outEntry := widget.NewEntry()
    chooseImg := widget.NewButton("Image", func() {
        dlg := dialog.NewFileOpen(func(uc fyne.URIReadCloser, err error) {
            if uc != nil {
                imgLabel.SetText(uc.URI().Path())
                uc.Close()
            }
        }, w)
        dlg.SetFilter(storage.NewExtensionFileFilter([]string{".png", ".jpg"}))
        dlg.Show()
    })
    chooseOut := widget.NewButton("Out", func() {
        dialog.NewFolderOpen(func(lu fyne.ListableURI, err error) {
            if lu != nil {
                outEntry.SetText(lu.Path())
            }
        }, w).Show()
    })
    genImg := widget.NewButton("Generate", func() {
        if imgLabel.Text == "(none)" || outEntry.Text == "" {
            dialog.ShowError(fyne.NewError("err", "missing input"), w)
            return
        }
        f, err := os.Open(imgLabel.Text)
        if err != nil {
            dialog.ShowError(err, w)
            return
        }
        defer f.Close()
        img, _, err := image.Decode(f)
        if err != nil {
            dialog.ShowError(err, w)
            return
        }
        outPath := filepath.Join(outEntry.Text, filepath.Base(imgLabel.Text))
        outFile, err := os.Create(outPath)
        if err != nil {
            dialog.ShowError(err, w)
            return
        }
        defer outFile.Close()
        png.Encode(outFile, img)
        dialog.ShowInformation("OK", "Saved "+outPath, w)
    })
    imgTab := container.NewVBox(
        container.NewHBox(chooseImg, imgLabel),
        container.NewHBox(outEntry, chooseOut),
        genImg)

    tabs := container.NewAppTabs(
        container.NewTabItem("Tree", treeTab),
        container.NewTabItem("Image", imgTab),
    )

    w.SetContent(tabs)
    w.Resize(fyne.NewSize(400, 300))
    w.ShowAndRun()
}
